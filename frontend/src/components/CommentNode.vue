<script setup>
import { ref, computed, nextTick } from 'vue'
import CommentItem from './CommentItem.vue'


// ---- Comment with answers
const props = defineProps({
  comment: { type: Object, required: true }, 
})

const emit = defineEmits(['reply']) 
// ---- Expandable answers
const isExpanded = ref(true)
const repContRef = ref(null)

const handleReply = (commentId) => {
  emit('reply', commentId)
}

// ---- Toggle + scroll to replies after expand
const handleToggle = async () => {
  isExpanded.value = !isExpanded.value
  if (isExpanded.value) {
    await nextTick()
    repContRef.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}

// ---- Recursively count all nested replies
const countAllReplies = (replies) => {
  if (!replies || replies.length === 0) return 0
  return replies.reduce((acc, reply) => {
    return acc + 1 + countAllReplies(reply.replies)
  }, 0)
}

const totalReplies = computed(() => countAllReplies(props.comment.replies))
</script>
<template>
  <div class="comm-n">
    <CommentItem
      :comment="comment"
      :repliesCount="totalReplies"
      :isExpanded="isExpanded"
      @reply="handleReply"
      @toggle="handleToggle"
    />
    <!--  Recursive rendering of responses if expanded -->
    <div
      v-if="isExpanded && comment.replies && comment.replies.length > 0"
      class="rep-cont"
      ref="repContRef"
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

<style lang="scss" src="../assets/styles/comment-node.scss"></style>
