<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
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
  X,
} from 'lucide-vue-next'
// ---- Import the comment service for API interactions
import { commentService } from '../services/commentService'

const props = defineProps({
  parentId: { type: Number, default: null },
})

const emit = defineEmits(['success', 'cancel-reply'])

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
  nickname: localStorage.getItem('user_nickname') || '',
  email: localStorage.getItem('user_email') || '',
  homepage: '',
  text: '',
  captcha_key: '',
  captcha_val: '',
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

// ---- Watch for parent ID changes
watch(
  () => props.parentId,
  (newParentId) => {
    if (newParentId) {
      formData.value.parent = newParentId
    }
  },
)

const cancelReply = () => {
  formData.value.parent = null
  emit('cancel-reply')
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
  console.log('FILE:', file)
  if (!file) return
  // ---- Check if the file is an image
  if (type === 'image') {
    const allowed = ['image/jpeg', 'image/png', 'image/gif']
    if (!allowed.includes(file.type)) {
      triggerAlert('Only allowed JPG, PNG, GIF')
      event.target.value = ''
      return
    }
    // ---- Check if the image is more than 10MB
    if (file.size > 10 * 1024 * 1024) {
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
    // Skip the files in this loop, process them separately
    if (key !== 'image' && key !== 'file' && val !== null && val !== '') {
      requestData.append(key, val)
    }
  })

  // ---- EXPRESSLY add files with their names (logic for Firefox)
  if (formData.value.image) {
    requestData.append('image', formData.value.image, formData.value.image.name)
  }
  if (formData.value.file) {
    requestData.append('file', formData.value.file, formData.value.file.name)
  }
  try {
    await commentService.createComment(requestData)
    // ---- Save user data to localStorage
    // ---- So that the user does not immediately enter his name and email
    localStorage.setItem('user_nickname', formData.value.nickname)
    localStorage.setItem('user_email', formData.value.email)
    // ---- Clear after success
    Object.assign(formData.value, {
      nickname: formData.value.nickname,
      email: formData.value.email,
      homepage: '',
      text: '',
      captcha_key: '',
      captcha_val: '',
      image: null,
      file: null,
      parent: null,
    })
    // ---- Clear the physical fields of file selection (via ref)
    if (imageInput.value) imageInput.value.value = ''
    if (fileInput.value) fileInput.value.value = ''
    // --- Show a success message and hide it
    showSuccess.value = true
    setTimeout(() => (showSuccess.value = false), 5000)

    featchCaptcha() // ---- Update the captcha
    emit('success')
  } catch (err) {
    if (err.response && err.response.data) {
      errors.value = err.response.data // ---- DRF returns validation errors
    }
    featchCaptcha() // ---- Update the captcha
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="submitForm" class="comm-f">
    <div v-if="formData.parent" class="rpl-inf">
      <span>Replying to comment #{{ formData.parent }}</span>
      <button type="button" @click="cancelReply" class="cancel-btn">
        <X :size="16" /> Cancel
      </button>
    </div>

    <div class="u-info">
      <div class="inp-gr">
        <input
          v-model="formData.nickname"
          placeholder="Nickname (Latin/Digits)"
          required
          pattern="^[a-zA-Z0-9]+$"
        />
        <span v-if="errors.nickname" class="err">{{ errors.nickname[0] }}</span>
      </div>
      <div class="inp-gr">
        <input
          v-model="formData.email"
          type="email"
          placeholder="E-mail"
          required
        />
        <span v-if="errors.email" class="err">{{ errors.email[0] }}</span>
      </div>
      <div class="inp-gr">
        <input
          v-model="formData.homepage"
          type="url"
          placeholder="Home page (optional)"
        />
        <span v-if="errors.homepage" class="err">{{ errors.homepage[0] }}</span>
      </div>
    </div>

    <div class="comm-e">
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

      <label class="fil-l" for="imageInput">
        <ImageIcon :size="18" />
      </label>
      <input
        id="imageInput"
        type="file"
        ref="imageInput"
        accept="image/*"
        @change="(e) => handlerFileChange(e, 'image')"
        style="display: none"
      />

      <label class="f-lbl" for="fileInput">
        <FileText :size="18" />
      </label>

      <input
        id="fileInput"
        type="file"
        ref="fileInput"
        accept=".txt"
        @change="(e) => handlerFileChange(e, 'file')"
        style="display: none"
      />
    </div>
    <textarea
      v-model="formData.text"
      ref="textareaRef"
      placeholder="Your message..."
      required
    ></textarea>
    <span v-if="errors.text" class="err">{{ errors.text[0] }}</span>

    <div class="cp-section">
      <div class="cp-img-wr">
        <img :src="captchaUrl" alt="captcha" class="cp-img" />
        <button type="button" @click="featchCaptcha" class="ref-btn">
          <RefreshCw :size="16" />
        </button>
      </div>
      <input v-model="formData.captcha_val" placeholder="Enter code" required />
      <span v-if="errors.captcha_val || errors.captcha" class="err">
        {{
          (errors.captcha_val ? errors.captcha_val[0] : '') ||
          (errors.captcha ? errors.captcha[0] : '')
        }}
      </span>
    </div>
    ``
    <div v-if="formData.text" class="pre-box">
      <p class="pre-titl">Preview:</p>
      <div v-html="previewHtml" class="pre-cntx"></div>
    </div>
    <transition-group name="fade">
      <p v-if="showSuccess" class="success-m">
        The comment has been successfully added to the database!
      </p>
      <p v-if="alertMessage" class="al-toast">{{ alertMessage }}</p>
    </transition-group>

    <button type="submit" :disabled="isSubmitting" class="sub-btn">
      <Send :size="18" /> {{ isSubmitting ? 'Sending...' : 'Post Comment' }}
    </button>
  </form>
</template>

<style scoped lang="scss" src="../assets/styles/comment-form.scss"></style>
