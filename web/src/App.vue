<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useCameraFeed } from './useCameraFeed'

const { cameras, frames, connected } = useCameraFeed()

// Buyutulmus gorunumdeki kameranin id'si (null = grid gorunumu)
const selectedId = ref(null)

const selectedIndex = computed(() => cameras.value.findIndex((c) => c.id === selectedId.value))
const selected = computed(() => cameras.value[selectedIndex.value] ?? null)

function open(id) {
  selectedId.value = id
}

function close() {
  selectedId.value = null
}

function step(delta) {
  const n = cameras.value.length
  if (!n || selectedIndex.value < 0) return
  selectedId.value = cameras.value[(selectedIndex.value + delta + n) % n].id
}

// Buyutulen kamera ayrilirsa gorunumu kapat
watch(cameras, () => {
  if (selectedId.value !== null && selectedIndex.value < 0) close()
})

function onKey(e) {
  if (selectedId.value === null) return
  if (e.key === 'Escape') close()
  else if (e.key === 'ArrowRight') step(1)
  else if (e.key === 'ArrowLeft') step(-1)
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <header class="topbar">
    <h1>Kamera Paylaşımı</h1>
    <span class="status" :class="{ on: connected }">
      {{ connected ? `${cameras.length} kamera bağlı` : 'Server bağlantısı yok…' }}
    </span>
  </header>

  <main>
    <p v-if="connected && !cameras.length" class="empty">
      Henüz bağlı kamera yok. Bir cihazda client'ı çalıştırın.
    </p>

    <div class="grid">
      <button v-for="cam in cameras" :key="cam.id" class="tile" @click="open(cam.id)">
        <img v-if="frames[cam.id]" :src="frames[cam.id]" :alt="cam.name" />
        <div v-else class="placeholder">Görüntü bekleniyor…</div>
        <span class="label">{{ cam.name }}</span>
      </button>
    </div>
  </main>

  <div v-if="selected" class="viewer" @click.self="close">
    <div class="viewer-head">
      <span>{{ selected.name }}</span>
      <span class="muted">{{ selectedIndex + 1 }} / {{ cameras.length }}</span>
      <button class="icon" title="Kapat (Esc)" @click="close">✕</button>
    </div>

    <div class="viewer-body">
      <button v-if="cameras.length > 1" class="nav" title="Önceki (←)" @click="step(-1)">‹</button>
      <img v-if="frames[selected.id]" :src="frames[selected.id]" :alt="selected.name" />
      <div v-else class="placeholder">Görüntü bekleniyor…</div>
      <button v-if="cameras.length > 1" class="nav" title="Sonraki (→)" @click="step(1)">›</button>
    </div>

    <div v-if="cameras.length > 1" class="strip">
      <button
        v-for="cam in cameras"
        :key="cam.id"
        class="thumb"
        :class="{ active: cam.id === selected.id }"
        @click="open(cam.id)"
      >
        <img v-if="frames[cam.id]" :src="frames[cam.id]" :alt="cam.name" />
        <span>{{ cam.name }}</span>
      </button>
    </div>
  </div>
</template>
