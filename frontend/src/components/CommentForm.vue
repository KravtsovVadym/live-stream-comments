<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
// ---- performs safe HTML cleanups
import DOMPurify from 'dompurify'
// ---- Import icons from the Lucide Vue library for the comment editor interface
import {
  Italic,
  Bold,
  Code,
  Link,
  Image as ImageIcon,
  FileText,
  Send,
  RefreshCw,
} from 'lucide-vue-next'
import { commentService } from '../services/commentService'

const textareaRef = ref(null)
const fileInput = ref(null)
const imageInput = ref(null)
const alertMessage = ref('')
// ---- Show an error message
const triggerAlert = (message) => {
  alertMessage.value = message
  // ---- Clear after 3 seconds
  setTimeout(() => {
    alertMessage.value = ''
  }, 3000)
}

const formData = ref({
  nickname: '',
  email: '',
  homepage: '',
  text: '',
  captcha_key: '',
  captcha_value: '',
  image: null,
  file: null,
  parent: null,
})

const captchaUrl = ref('')
const errors = ref({})
const showSuccess = ref(false)
const isSubmitting = ref(false) // ---- unlock buttonу

// ---- Getting a captcha when loading
const featchCaptcha = async () => {
  try {
    const { data } = await commentService.getCaptcha()
    captchaUrl.value = data.image_url
    formData.value.captcha_key = data.key
  } catch (err) {
    console.error('Error loading captcha', err)
  }
}

// ---- Getting a captcha when loading
onMounted(featchCaptcha)

// ---- Reactive preview of the comment and performs safe HTML cleanups
const previewHtml = computed(() => {
  return DOMPurify.sanitize(formData.value.text, {
    ALLOWED_TAGS: ['a', 'code', 'i', 'strong'],
    ALLOWED_ATTR: ['href', 'title'],
  })
})

// ---- Reviewing and tagging a comment
const insertTag = (tag) => {
  const elem = textareaRef.value
  const start = elem.selectionStart
  const end = elem.selectionEnd
  const content = formData.value.text
  const selected = content.substring(start, end)

  let result =
    tag === 'a'
      ? `<a href="" title="">${selected || 'link'}</a>`
      : `<${tag}>${selected}</${tag}>`

  formData.value.text = // ---- add a tag to a comment
    content.substring(0, start) + result + content.substring(end)

  nextTick(() => {
    // ---- move the cursor
    const newPos = start + result.length
    elem.setSelectionRange(newPos, newPos)
    elem.focus()
  })
}
// ---- Frontend validation files
const handlerFileChange = (event, type) => {
  const file = event.target.files[0]
  if (!file) return
  // ---- Check if the file is an image
  if (type === 'image') {
    const allowed = ['image/jpeg', 'image/png', 'image/gif']
    if (!allowed.includes(file.type)) {
      triggerAlert('Only allowed JPG, PNG, GIF')
      event.target.value = ''
      return
    }
    // ---- Check if the image is more than 5MB
    if (file.size > 5 * 1024 * 1024) {
      triggerAlert('image too large (max 5MB)')
      event.target.value = ''
      return
    }
    formData.value.image = file
    //--------------------------------------
    // ---- Check if the file is a TXT
  } else if (type === 'file') {
    const allowed = 'text/plain'
    if (!allowed.includes(file.type)) {
      triggerAlert('Only allowed TXT files')
      event.target.value = ''
      return
    }
    // ---- Check if the file is more than 100KB
    if (file.size > 100 * 1024) {
      errors.value = 'File too large (max 100KB)'
      event.target.value = ''
      return
    }
    formData.value.file = file
  }
}

// ---- Form submission
const submitForm = async () => {
  errors.value = {}
  isSubmitting.value = true
  const requestData = new FormData()

  Object.entries(formData.value).forEach(([key, val]) => {
    if (val !== null && val !== '') requestData.append(key, val)
  })

  try {
    await commentService.createComment(requestData)
    // ---- Clear after success
    Object.assign(formData.value, {
      nickname: '',
      email: '',
      homepage: '',
      text: '',
      captcha_key: '',
      image: null,
      file: null,
      parent: null,
    })
    // ---- Clear the physical fields of file selection (via ref)
    if (imageInput.value) imageInput.value.value = ''
    if (fileInput.value) fileInput.value.value = ''
    // --- Show a success message and hide it
    showSuccess.value = true
    setTimeout(() => (showSuccess.value = false), 3000)

    featchCaptcha() // ---- Update the captcha
  } catch (err) {
    if (err.response && err.response.data) {
      console.log(err.response.data)
      errors.value = err.response.data // ---- DRF returns validation errors here
    }
    featchCaptcha() // ---- Update the captcha
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="submitForm" class="comment-form">
    <div class="user-info">
      <div class="input-group">
        <input
          v-model="formData.nickname"
          placeholder="Nickname (Latin/Digits)"
          required
          pattern="^[a-zA-Z0-9]+$"
        />
        <span v-if="errors.nickname" class="error">{{
          errors.nickname[0]
        }}</span>
      </div>
      <div class="input-group">
        <input
          v-model="formData.email"
          type="email"
          placeholder="E-mail"
          required
        />
        <span v-if="errors.email" class="error">{{ errors.email[0] }}</span>
      </div>
      <div class="input-group">
        <input
          v-model="formData.homepage"
          type="url"
          placeholder="Home page (optional)"
        />
        <span v-if="errors.homepage" class="error">{{
          errors.homepage[0]
        }}</span>
      </div>
    </div>

    <div class="comment-editor">
      <button type="button" @click="insertTag('strong')">
        <Bold :size="18" />
      </button>
      <button type="button" @click="insertTag('i')">
        <Italic :size="18" />
      </button>
      <button type="button" @click="insertTag('code')">
        <Code :size="18" />
      </button>
      <button type="button" @click="insertTag('a')">
        <Link :size="18" />
      </button>
      <label class="file-label">
        <ImageIcon :size="18" />
        <input
          type="file"
          ref="imageInput"
          @change="(event) => handlerFileChange(event, 'image')"
          accept="image/*"
          hidden
        />
      </label>
      <label class="file-label">
        <FileText :size="18" />
        <input
          type="file"
          ref="fileInput"
          @change="(event) => handlerFileChange(event, 'file')"
          accept=".txt"
          hidden
        />
      </label>
    </div>
    <textarea
      v-model="formData.text"
      ref="textareaRef"
      placeholder="Your message..."
      required
    ></textarea>
    <span v-if="errors.text" class="errors">{{ errors.text[0] }}</span>

    <div class="captcha-section">
      <div class="captcha-img-wrapper">
        <img :src="captchaUrl" alt="captcha" class="captcha-img" />
        <button type="button" @click="featchCaptcha" class="refresh-btn">
          <RefreshCw :size="16" />
        </button>
      </div>
      <input
        v-model="formData.captcha_value"
        placeholder="Enter code"
        required
      />
      <span v-if="errors.captcha_value || errors.captcha" class="error">
        {{
          (errors.captcha_value ? errors.captcha_value[0] : '') ||
          (errors.captcha ? errors.captcha[0] : '')
        }}
      </span>
    </div>
    <div v-if="formData.text" class="preview-box">
      <p class="preview-title">Preview:</p>
      <div v-html="previewHtml" class="preview-content"></div>
    </div>
    <transition-group name="fade">
      <p v-if="showSuccess" class="success-message">
        The comment has been successfully added to the database!
      </p>
      <p v-if="alertMessage" class="alert-toast">{{ alertMessage }}</p>
    </transition-group>

    <button type="submit" :disabled="isSubmitting" class="submit-btn">
      <Send :size="18" /> {{ isSubmitting ? 'Sending...' : 'Post Comment' }}
    </button>
  </form>
</template>

<style scoped lang="scss" src="../assets/styles/comment-form.scss"></style>
