<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute } from "vue-router";

interface RecipeDetail {
  recipe_id: string;
  name: string;
  description: string;
  ingredients: string[];
  instructions: string[];
  image_urls: string[];
}

export default defineComponent({
  name: "RecipePage",
  setup() {
    const route = useRoute();
    const recipe = ref<RecipeDetail | null>(null);
    const isLoading = ref<boolean>(true);
    const errorMessage = ref<string | null>(null);
    
    const fetchRecipe = async () => {
      isLoading.value = true;
      errorMessage.value = null;

      try {
        const response = await fetch(`http://localhost:5000/recipe/${route.params.id}`, {
          method: "GET",
          headers: {
            "Authorization": "dev", // Send the authorization token
          },
          credentials: "include", // If session-based auth is used
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        recipe.value = data;
      } catch (error) {
        errorMessage.value = (error as Error).message;
      } finally {
        isLoading.value = false;
      }
    };

    onMounted(fetchRecipe);

    return {
      recipe,
      isLoading,
      errorMessage,
    };
  },
});
</script>

<template>
  <div class="recipe-page">
    <h1>Recipe Details</h1>

    <div v-if="isLoading">Loading...</div>
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <div v-if="recipe" class="recipe-details">
      <h2>{{ recipe.name }}</h2>
      
      <div v-if="recipe.image_urls.length" class="image-gallery">
        <img v-for="url in recipe.image_urls" :key="url" :src="url" :alt="recipe.name" />
      </div>

      <h3>Description</h3>
      <p>{{ recipe.description }}</p>

      <h3>Ingredients</h3>
      <ul>
        <p>{{ recipe.ingredients }}</p>
      </ul>

      <h3>Instructions</h3>
      <ol>
        {{ recipe.instructions }}
      </ol>
    </div>
  </div>
</template>

<style scoped>
.recipe-page {
  max-width: 800px;
  margin: auto;
  padding: 20px;
}

.image-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-gallery img {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
}

.error {
  color: red;
}
</style>
