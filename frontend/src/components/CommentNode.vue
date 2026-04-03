<script setup>
import { ref } from 'vue'
import CommentItem from './CommentItem.vue'
import { ChevronDown, ChevronRight } from 'lucide-vue-next'


// ---- Comment with answers
defineProps({
  comment: { type: Object, required: true }, 
})

const emit = defineEmits(['reply']) 
// ---- Expandable answers
const isExpanded = ref(true) 

const handleReply = (commentId) => {
  emit('reply', commentId)
}
</script>
<template>
  <div class="comm-n">
    
    <CommentItem :comment="comment" @reply="handleReply" />
    <!-- Expand/collapse answers button -->
    <div v-if="comment.replies && comment.replies.length > 0" class="rep-head">
      <button @click="isExpanded = !isExpanded" class="togg-btn">
        <ChevronDown v-if="isExpanded" :size="18" />
        <ChevronRight v-else :size="18" />
        <span
          >{{ comment.replies.length }}
          {{ comment.replies.length === 1 ? 'reply' : 'replies' }}</span
        >
      </button>
    </div>
    <!--  Recursive rendering of responses if expanded -->
    <div
      v-if="isExpanded && comment.replies && comment.replies.length > 0"
      class="rep-cont"
    >
      <CommentNode
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        @reply="handleReply"
      />
    </div>
  </div>
</template>

<style scoped lang="scss" src="../assets/styles/comment-node.scss"></style>
