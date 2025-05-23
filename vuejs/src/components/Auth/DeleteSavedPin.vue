<script setup>
import { onMounted, ref, computed, onActivated, onDeactivated } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import axios from 'axios';

onActivated(() => {
  if (videoPlayer.value) {
    var playPromise = videoPlayer.value.play()
    if (playPromise !== undefined) {
      playPromise.then(_ => {
        // Automatic playback started!
        // Show playing UI.
      })
        .catch(error => {
          // Auto-play was prevented
          // Show paused UI.
        });
    }
  }
});

onDeactivated(() => {
  if (videoPlayer.value) {
    // Можно остановить видео или выполнить другие действия
    videoPlayer.value.pause();
  }
});


const popUser = ref(null)
const popImage = ref(null)
const popBanner = ref(null)

const emit = defineEmits(['pinLoaded'])

const user = ref(null);
const pinImage = ref(null);
const pinVideo = ref(null)
const imageLoaded = ref(false); // Флаг загрузки изображения
const videoLoaded = ref(false); // Флаг загрузки видео

const userImage = ref(null);

const showPopover = ref(false); // State to control the popover visibility

const insidePopover = ref(false)

const bgSave = ref('bg-black')
const saveText = ref('Delete')

const props = defineProps({
  pin: Object,
  showAllPins: Boolean,
});

const onImageLoad = () => {
  imageLoaded.value = true;
  emit('pinLoaded')
};

const onVideoLoad = () => {
  if (videoPlayer.value) {
    videoDuration.value = videoPlayer.value.duration; // Получаем длительность
  }
  videoLoaded.value = true;
  emit('pinLoaded')
}

const videoDuration = ref(0)
const currentTime = ref(0)

const videoPlayer = ref(null);

const imageGif = ref(false)


const onTimeUpdate = () => {
  if (videoPlayer.value) {
    currentTime.value = videoPlayer.value.currentTime; // Получаем текущее время
  }
};

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${String(minutes).padStart(1, '0')}:${String(secs).padStart(2, '0')}`;
};

const formattedTimeRemaining = computed(() => {
  const timeRemaining = Math.max(videoDuration.value - currentTime.value, 0);
  return formatTime(timeRemaining);
});

const showSaveButton = ref(false)


onMounted(async () => {

  try {
    const response = await axios.get(`/api/users/user_id/${props.pin.user_id}`);
    user.value = response.data;

    try {
      const userResponse = await axios.get(`/api/users/upload/${user.value.id}`, { responseType: 'blob' });
      const blobUrl = URL.createObjectURL(userResponse.data);
      userImage.value = blobUrl;
    } catch (error) {
      console.error(error);
    }

    try {
      const pinResponse = await axios.get(`/api/pins/upload/${props.pin.id}`, { responseType: 'blob' });
      const blobUrl = URL.createObjectURL(pinResponse.data);
      const contentType = pinResponse.headers['content-type'];
      if (contentType === 'image/gif') {
        imageGif.value = true
      }
      if (contentType.startsWith('image/')) {
        pinImage.value = blobUrl;
      } else {
        pinVideo.value = blobUrl;
      }
    } catch (error) {
      console.error(error);
    }
  } catch (error) {
    console.error(error);
  }
});

async function loadUser() {
  try {
    const response = await axios.get(`/api/users/user_id/${props.pin.user_id}`)
    popUser.value = response.data
    try {
      const response = await axios.get(`/api/users/upload/${props.pin.user_id}`, { responseType: 'blob' })
      const blobUrl = URL.createObjectURL(response.data);
      popImage.value = blobUrl
    } catch (error) {
      console.error(error)
    }
  } catch (error) {
    console.error(error)
  }
  if (popUser.value && popUser.value.banner_image) {
    try {
      const userResponse = await axios.get(
        `/api/users/upload/banner/${popUser.value.id}`,
        {
          responseType: 'blob', // Treat the response as a binary file
          withCredentials: true, // Include credentials such as cookies or client certificates
        }
      );
      const blobUrl = URL.createObjectURL(userResponse.data);
      popBanner.value = blobUrl;
    } catch (error) {
      console.error(error);
    }
  }
}

async function save() {
  bgSave.value = 'bg-black'
  try {
    const response = await axios.delete(`/api/pins/user_saved_pins/${props.pin.id}`, {
      withCredentials: true
    })
    saveText.value = 'Deleted'

  } catch (error) {
    console.error(error)
  }
}

</script>

<template>
  <div class="w-1/5 p-2">
    <div class="relative block transition-transform duration-100 transform hover:scale-105" @mouseover="showSaveButton = true; "
      @mouseleave="showSaveButton = false; ">
      <button v-if="showSaveButton" @click.stop="save"
        :class="`absolute z-50 top-2 right-2 px-6 py-3 text-sm ${bgSave} hover:bg-red-800 text-white rounded-3xl transition`">
        {{ saveText }}
      </button>
      <RouterLink :to="`/pin/${pin.id}`">
        <div v-show="!showAllPins" :class="['w-full', 'rounded-3xl']"
          :style="{ backgroundColor: pin.rgb, height: pin.height + 'px' }">
        </div>
        <div class="relative">
          <div v-if="imageGif" class="absolute top-2 left-2 bg-gray-200 text-black rounded-2xl px-3 py-1 text-sm">Gif
          </div>
          <img v-show="showAllPins && pinImage" :src="pinImage" @load="onImageLoad" alt="pin image"
            class="w-full h-auto rounded-3xl" />
        </div>
        <div class="relative">
          <div v-if="videoDuration" class="absolute top-2 left-2 bg-gray-200 text-black rounded-2xl px-3 py-1 text-sm">
            {{ formattedTimeRemaining }}
          </div>
          <video v-show="showAllPins && pinVideo" :src="pinVideo" @loadeddata="onVideoLoad" ref="videoPlayer"
            @timeupdate="onTimeUpdate" class="w-full h-auto rounded-3xl" autoplay loop muted />
        </div>
      </RouterLink>
    </div>

    <p v-if="pin.title" class="mt-2 text-sm"> {{ pin.title }}</p>

    <RouterLink v-if="user" :to="`/user/${user.username}`" 
      class="flex items-center mt-2 hover:underline cursor-pointer relative ">
      <div v-if="!showAllPins" class="bg-gray-300 w-8 h-8 rounded-full"></div>
      <img v-else :src="userImage" alt="user profile" class="w-8 h-8 rounded-full object-cover" />
      <span v-if="user && showAllPins" class="ml-2 text-sm font-medium"> {{ user.username }}</span>
    </RouterLink>

    <div v-else class="flex items-center mt-2 hover:underline cursor-pointer">
      <div class="bg-gray-300 w-8 h-8 rounded-full"></div>
      <span class="ml-2 text-sm font-medium"></span>
    </div>
  </div>
</template>


<style scoped>
.flash-enter-active {
  animation: flashEffect 1s ease-out;
}

.flash-enter-from,
.flash-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

@keyframes flashEffect {
  0% {
    opacity: 0;
    transform: scale(0.9);
    filter: brightness(0.1);
  }

  50% {
    opacity: 1;
    transform: scale(1);
    filter: brightness(1.2);
  }

  100% {
    opacity: 1;
    transform: scale(1);
    filter: brightness(1);
  }
}
</style>