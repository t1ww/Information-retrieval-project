<script lang="ts">
import { defineComponent } from "vue";
import NavBar from "./components/NavBar.vue";
import Logo from "./components/Logo.vue";

export default defineComponent({
  name: "App",
  components: {
    NavBar,
    Logo,
  },
});
</script>

<template>
  <!-- NavBar component -->
  <NavBar class="hover-color" />
  <!-- Router-view where route components will be rendered -->
  <router-view />
</template>