import { ref, computed } from 'vue'
import { commentService } from '../services/commentService'

export function useCommentData() {
  const flatComments = ref([])
  const currentPage = ref(1)
  const totalPages = ref(1)
  const ordering = ref('-created_at')
  const PAGE_SIZE = 25

  // ---- commentTree just passes flatComments (for v-for)
  const commentTree = computed(() => flatComments.value)

  // ---- loads comments from the paginated API
  const loadComments = async (page = 1) => {
    try {
      const { data } = await commentService.getComments(page, ordering.value)
      flatComments.value = data.results
      totalPages.value = Math.ceil(data.count / PAGE_SIZE)
      currentPage.value = page
    } catch (err) {
      console.error('Failed to load comments:', err)
    }
  }

  const addCommentToTree = (newComment) => {
    if (newComment.parent === null) {
      // ----root comment: add to the top of the list
      const exists = flatComments.value.some((c) => c.id === newComment.id)
      if (!exists) {
        flatComments.value.unshift(newComment)
      }
    } else {
      // ---- answer: we search for the father recursively
      const findAndAddReply = (comments) => {
        for (let comment of comments) {
          // ---- found the father for the answer
          if (comment.id === newComment.parent) {
            if (!comment.replies) comment.replies = []
            const replyExists = comment.replies.some(
              (r) => r.id === newComment.id,
            )
            if (!replyExists) {
              comment.replies.unshift(newComment)
            }
            return true
          }
          // ---- recursive search in nested responses
          if (comment.replies && findAndAddReply(comment.replies)) {
            return true
          }
        }
        return false
      }
      findAndAddReply(flatComments.value)
    }
  }

  const sortBy = (field) => {
    ordering.value = field
    loadComments(1)
  }

  return {
    flatComments,
    currentPage,
    totalPages,
    ordering,
    commentTree,
    loadComments,
    addCommentToTree,
    sortBy,
  }
}
