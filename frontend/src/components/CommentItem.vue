<script setup>
import { computed, ref } from 'vue'
import lightbox from 'lightbox2'
import 'lightbox2/dist/css/lightbox.css'

import { FileText } from 'lucide-vue-next'
import DOMPurify from 'dompurify'
import FileModal from './FileModal.vue'

const props = defineProps({
  // ---- The object of the comment
  comment: { type: Object, required: true },
})

const emit = defineEmits(['reply'])

const isFileModalOpen = ref(false)
const selectedFileUrl = ref('')
const selectedFileName = ref('')

// ---- Cleaning HTML from XSS security
const cleanText = computed(() =>
  DOMPurify.sanitize(props.comment.text, {
    ALLOWED_TAGS: ['i', 'strong', 'a', 'code'],
    ALLOWED_ATTR: ['href', 'title'],
  }),
)

const formattedDate = computed(() => {
  const date = new Date(props.comment.created_at)
  const formatter = new Intl.DateTimeFormat('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
  return formatter.format(date)
})

//  ---- Opening a modal window with a file
const openFileModal = (fileUrl, fileName) => {
  selectedFileUrl.value = fileUrl
  selectedFileName.value = fileName
  isFileModalOpen.value = true
}

const avatarUrl = computed(
  () => `https://robohash.org/${props.comment.email}?set=set2&size=30x30`,
)
</script>

<template>
  <div class="comm-item">
    <img :src="avatarUrl" class="avatar" alt="avatar" width="30" height="30" />
    <div class="comm-cont">
      <!-- Header: nickname, email, date -->
      <div class="comm-head">
        <span class="nick">{{ comment.nickname }}</span>
        <span class="email">{{ comment.email }}</span>
        <span class="date">{{ formattedDate }}</span>
      </div>
      <!-- comment text purified via DOMPurify -->
      <div class="comm-tx" v-html="cleanText"></div>

      <div v-if="comment.image || comment.file" class="comm-mda">
        <!-- Image from lightbox -->
        <a
          v-if="comment.image"
          :href="comment.image"
          data-lightbox="gallery"
          :data-title="comment.nickname"
        >
          <img
            :src="comment.image"
            class="comm-img"
            alt="User attachment"
            loading="lazy"
          />
        </a>

        <!-- file link opens a modal window -->
        <a
          v-if="comment.file"
          @click="openFileModal(comment.file, 'file.txt')"
          class="f-link"
          style="cursor: pointer"
        >
          <FileText :size="16" />
          View file
        </a>
      </div>
      <!-- Reply button -->
      <button class="r-btn" @click="emit('reply', comment.id)">Reply</button>
    </div>
  </div>
  <!-- Modal window for viewing files -->
  <FileModal
    :isOpen="isFileModalOpen"
    :fileUrl="selectedFileUrl"
    :fileName="selectedFileName"
    @close="isFileModalOpen = false"
  />
</template>
<style scoped lang="scss" src="../assets/styles/comment-item.scss"></style>
