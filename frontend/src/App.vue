<script setup>
import { ref, nextTick } from 'vue'
import CommentForm from './components/CommentForm.vue'
import CommentList from './components/CommentList.vue'

// ---- Comment ID to reply to
const parentIdForReply = ref(null)
// ---- Link to scroll form
const formRef = ref(null)

// ---- Sets the parent comment and scrolls to the form
const handleReply = (id) => {
  parentIdForReply.value = id
  nextTick(() => {
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      nextTick(() => {
        formRef.value?.focusTextarea()
      })
    }, 50)
  })
}

// ---- Scroll to parent comment after successful addition
const handleCommentSuccess = (parentId) => {
  if (parentId) {
    nextTick(() => {
      document
        .getElementById(`comment-${parentId}`)
        ?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    })
  }
}
</script>

<template>
  <div class="app-wrapper">
    <section class="hero-section">
      <div class="container py-5">
        <div class="text-center mb-4">
          <h1 class="hero-title">
            Join the <span class="gradient-text">Conversation</span>
          </h1>
          <p class="hero-sub mx-auto">
            Share your thoughts, ask questions, and connect with the community.
          </p>
        </div>
        <!-- Form card section -->
        <div class="form-card mx-auto">
          <div class="d-flex align-items-center gap-2 mb-3">
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
              class="lucide lucide-message-square w-5 h-5"
              aria-hidden="true"
              style="color: rgb(122, 62, 240)"
            >
              <path
                d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              ></path>
            </svg>
            <span class="fw-semibold text-light">Join the discussion</span>
          </div>
          <CommentForm
            ref="formRef"
            :parent-id="parentIdForReply"
            @success="handleCommentSuccess"
            @cancel-reply="parentIdForReply = null"
          />
        </div>
      </div>
      <div class="hero-fade"></div>
    </section>

    <!-- Comments list section -->
    <section class="list-section">
      <div class="container pb-5">
        <CommentList ref="commentListRef" @open-reply="handleReply" />
      </div>
    </section>
  </div>
  <footer class="app-footer">
    <p>© 2026 Developer by Vadym Kravtsov</p>
  </footer>
</template>
