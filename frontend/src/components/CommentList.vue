<script setup>
import { onMounted} from 'vue'
import CommentNode from './CommentNode.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useCommentData } from '../composables/useCommentData'

// ---- WebSocket URL from .env file
const VITE_WS_URL = import.meta.env.VITE_WS_URL

const {
  commentTree,
  loadComments,
  addCommentToTree,
  sortBy,
  totalPages,
  currentPage,
} = useCommentData()

const handleNewComment = (data) => {
  if (data.type === 'comment_created' && data.comment) {
    addCommentToTree(data.comment)
  }
}

// ---- Connect to WebSocket server and listen for new comments
const { socket } = useWebSocket(VITE_WS_URL, handleNewComment)

onMounted(() => {
  loadComments()
})

const emit = defineEmits(['open-reply'])
const handleReply = (parentId) => {
  emit('open-reply', parentId)
}

//  ---- Sorting methods call sortBy with a field
const sortByNickname = () => sortBy('nickname')
const sortByEmail = () => sortBy('email')
const sortByNewest = () => sortBy('-created_at')
const sortByOldest = () => sortBy('created_at')

defineExpose({
  loadComments,
})
</script>

<template>
  <div class="comm-wrp">
        <div class="pgn" v-if="totalPages > 1">
      <button
        v-for="p in totalPages"
        :key="p"
        @click="loadComments(p)"
        :class="{ active: p === currentPage }"
      >
        {{ p }}
      </button>
    </div>
    <br>
    <div class="sort-bar">
      <button @click="sortByNickname">User Name</button>
      <button @click="sortByEmail">Email</button>
      <button @click="sortByNewest">Newest First</button>
      <button @click="sortByOldest">Oldest First</button>
    </div>
    
    <!-- ---- Comment tree CommentNode recursive component -->
    <div class="comm-tree">
      <CommentNode
        v-for="comment in commentTree"
        :key="comment.id"
        :comment="comment"
        @reply="handleReply"
      />
    </div>
    <!-- Pagination displayed only if pages > 1 -->
    <div class="pgn" v-if="totalPages > 1">
      <button
        v-for="p in totalPages"
        :key="p"
        @click="loadComments(p)"
        :class="{ active: p === currentPage }"
      >
        {{ p }}
      </button>
    </div>
  </div>
</template>

<style lang="scss" src="../assets/styles/comment-list.scss"></style>
