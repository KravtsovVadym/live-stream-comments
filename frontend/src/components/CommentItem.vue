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
  // ---- Replies count for toggle button
  repliesCount: { type: Number, default: 0 },
  // ---- Whether to display replies or not
  isExpanded: { type: Boolean, default: true },
  // ---- Whether this is a nested reply
  isReply: { type: Boolean, default: false },
})

const emit = defineEmits(['reply', 'toggle'])

const isFileModalOpen = ref(false)
const selectedFileUrl = ref('')
const selectedFileName = ref('')

// ---- Cleaning HTML from XSS security
const cleanText = computed(() => {
  const withBreaks = props.comment.text.replace(/\n/g, '<br>')
  return DOMPurify.sanitize(withBreaks, {
    ALLOWED_TAGS: ['i', 'strong', 'a', 'code', 'br'],
    ALLOWED_ATTR: ['href', 'title'],
  })
})

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
  <div>
    <div
      :id="`comment-${comment.id}`"
      :class="['comm-item', { 'comm-item--reply': isReply }]"
    >
      <img
        :src="avatarUrl"
        class="avatar"
        alt="avatar"
        width="30"
        height="30"
      />
      <div class="comm-cont">
        <!-- Header: nickname, email, date -->
        <div class="comm-head">
          <span class="nick">{{ comment.nickname }}</span>
          <span class="email">{{ comment.email }}</span>
          <a class="home-page" target="_blank" :href="comment.homepage">{{
            comment.homepage
          }}</a>
          <span class="date">{{ formattedDate }}</span>
        </div>
        <!-- Body text  + image -->
        <div class="comm-body" :class="{ 'has-image': comment.image }">
          <div class="comm-tx-wrap">
            <!-- comment text purified via DOMPurify -->
            <div class="comm-tx" v-html="cleanText"></div>
            <!-- file link below text -->
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
          <!-- Image block -->
          <div v-if="comment.image" class="comm-img-wrap">
            <a
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
          </div>
        </div>
        <!-- Bottom actions: toggle replies -->
        <div class="comm-actions">
          <button
            v-if="repliesCount > 0"
            class="togg-btn"
            @click="emit('toggle')"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="lucide lucide-message-circle w-3.5 h-3.5"
              aria-hidden="true"
            >
              <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"></path>
            </svg>
            {{ repliesCount }}
          </button>
          <button class="r-btn r-btn--right" @click="emit('reply', comment.id)">
            Reply
          </button>
        </div>
      </div>
    </div>
    <!-- Modal window for viewing files -->
    <FileModal
      :isOpen="isFileModalOpen"
      :fileUrl="selectedFileUrl"
      :fileName="selectedFileName"
      @close="isFileModalOpen = false"
    />
  </div>
</template>

<style lang="scss" src="../assets/styles/comment-item.scss"></style>
