<script lang="ts">
import { defineComponent } from "vue";
import Logo from "@/components/Logo.vue";
import SearchBar from "@/components/SearchBar.vue";

export default defineComponent({
  components: {
    SearchBar,
    Logo
  },
  data() {
    return {
      playSound: true,  // Only play the sound for the homepage logo
    };
  },
});
</script>

<template>
  <Logo :play-sound="playSound" />
  <h1>Welcome to recipe browser</h1>
  <p>Start searching below!</p>
  <!-- Use the SearchBar component -->
  <SearchBar />
</template>

<style scoped>
/* Add your styles for the HomePage if needed */
</style>
