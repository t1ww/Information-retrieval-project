<template>
  <div>
    <img
      src="@/assets/images/croisshark no bg.png"
      class="logo hover-color"
      alt="logo"
      @click="onClick"
    />
  </div>
</template>

<script lang="ts">
import squeakSound from "@/assets/sounds/squeak.mp3";
import type { PropType } from "vue";

export default {
  props: {
    playSound: {
      type: Boolean as PropType<boolean>,
      default: false,
    },
  },
  methods: {
    onClick() {
      const logo = document.querySelector(".logo") as HTMLElement;
      logo.classList.add("shrink");

      if (this.playSound) {
        // Play squeak sound
        const sound = new Audio(squeakSound);

        // Adjust volume (between 0.0 and 1.0)
        sound.volume = 0.2; // 50% volume (you can adjust this)

        // Randomize pitch by changing playbackRate
        sound.playbackRate = 1 + (Math.random() * 1 - 0.4); // Randomize length

        // Randomize pitch by adjusting the playback rate
        const randomPitch = 1 + (Math.random() * 0.4 - 0.2); // Random pitch
        sound.playbackRate = randomPitch;

        sound.play();

        // Remove the shrinking animation after it completes (0.1s duration)
        setTimeout(() => {
          logo.classList.remove("shrink");
        }, 100); // Match the duration of the shrink animation
      }
    },
  },
};
</script>

<style scoped>
.logo {
  height: 10em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 100ms, transform 0.1s ease-in-out;
}

.hover-color:hover {
  filter: drop-shadow(0 0 2em #ff863642);
}

.shrink {
  transform: scale(0.8); /* Shrink the image to 80% of its original size */
}
</style>
