<script setup>
import { X } from 'lucide-vue-next'
import { ref, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  fileUrl: String,
  fileName: String,
})

const emit = defineEmits(['close'])
const fileContent = ref('')
const isLoading = ref(true)

const handleClose = () => {
  emit('close')
}
// ---- Load the contents of the file into the modal
const loadTextFile = async () => {
  if (!props.fileUrl) {
    return
  }

  isLoading.value = true
  try {
    const response = await fetch(
      `/api/proxy-file/?url=${encodeURIComponent(props.fileUrl)}`,
    )
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    // ---- Save the contents of the file to a constant
    const text = await response.text()
    fileContent.value = text
  } catch (e) {
    console.error('Error loading file:', e)
    fileContent.value = 'Error loading file'
  } finally {
    isLoading.value = false
  }
}
// ---- Reload the file content whenever the fileUrl changes
watch(
  () => props.isOpen,
  (val) => {
    if (val) {
      loadTextFile()
    }
  },
)
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ fileName }}</h2>
        <button class="close-btn" @click="handleClose">
          <X :size="20" />
        </button>
      </div>
      <div class="txt-view">
        <div v-if="isLoading" class="load">Loading...</div>
        <pre v-else>{{ fileContent }}</pre>
      </div>
    </div>
  </div>
</template>

<style lang="scss" src="../assets/styles/file-modal.scss"></style>
