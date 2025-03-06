<template>
  <div>
    <h1>Recipe Page</h1>
    <p>Recipe ID: {{ recipeId }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useRoute } from "vue-router";

export default defineComponent({
  name: "RecipePage",
  setup() {
    const route = useRoute();
    const recipeId = route.params.id; // Accessing the dynamic parameter

    return {
      recipeId,
    };
  },
});
</script>
