<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute } from "vue-router";

interface RecipeDetail {
  recipe_id: string;
  name: string;
  description: string;
  ingredients: string;
  instructions: string;
  image_urls: string[];
}

export default defineComponent({
  name: "RecipePage",
  setup() {
    const route = useRoute();
    const recipe = ref<RecipeDetail | null>(null);
    const isLoading = ref<boolean>(true);
    const errorMessage = ref<string | null>(null);
    const currentImageIndex = ref<number>(0);
    const fallbackImage = ref<string>("");

    const fetchFallbackImage = async (): Promise<string> => {
      try {
        const response = await fetch(
          `http://localhost:5000/search_nearest_image?query=${encodeURIComponent(recipe.value?.name || "")}`,
          {
            method: "GET",
            headers: {
              "Authorization": "dev", // Send the authorization token
            },
            credentials: "include",
          }
        );
        if (!response.ok) {
          throw new Error(`Error fetching image: ${response.status} ${response.statusText}`);
        }
        const imageData = await response.json();
        if (imageData.result && imageData.result.image_urls && imageData.result.image_urls.length > 0) {
          return imageData.result.image_urls[0];
        }
        return "";
      } catch (error) {
        console.error("Error fetching fallback image:", error);
        return "";
      }
    };

    const fetchRecipe = async () => {
      isLoading.value = true;
      errorMessage.value = null;
      try {
        const response = await fetch(`http://localhost:5000/recipe/${route.params.id}`, {
          method: "GET",
          headers: {
            "Authorization": "dev", // Send the authorization token
          },
          credentials: "include",
        });
        if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        recipe.value = data;
        if (!data.image_urls || data.image_urls.length === 0) {
          fallbackImage.value = await fetchFallbackImage();
        }
      } catch (error) {
        errorMessage.value = (error as Error).message;
      } finally {
        isLoading.value = false;
      }
    };

    const nextImage = () => {
      if (recipe.value && recipe.value.image_urls.length > 0) {
        currentImageIndex.value = (currentImageIndex.value + 1) % recipe.value.image_urls.length;
      }
    };

    const prevImage = () => {
      if (recipe.value && recipe.value.image_urls.length > 0) {
        currentImageIndex.value = (currentImageIndex.value - 1 + recipe.value.image_urls.length) % recipe.value.image_urls.length;
      }
    };

    const setImage = (index: number) => {
      currentImageIndex.value = index;
    };

    onMounted(fetchRecipe);

    return {
      recipe,
      isLoading,
      errorMessage,
      currentImageIndex,
      nextImage,
      prevImage,
      setImage,
      fallbackImage,
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

      <div class="carousel">
        <button v-if="recipe.image_urls.length > 1" class="prev" @click="prevImage">&#10094;</button>
        <div v-if="recipe.image_urls.length" class="carousel-image-container">
          <transition name="fade" mode="out-in">
            <img :key="currentImageIndex" :src="recipe.image_urls[currentImageIndex]" :alt="recipe.name"
              class="carousel-image" />
          </transition>
        </div>

        <!-- Fallback Image Section with Overlay -->
        <div v-else class="fallback-container">
          <img :src="fallbackImage" alt="Fallback Recipe Image" class="carousel-image" />
          <div class="overlay">
            <span>*Taken from nearest image</span>
          </div>
        </div>

        <button v-if="recipe.image_urls.length > 1" class="next" @click="nextImage">&#10095;</button>

        <!-- Indicators -->
        <div class="indicators">
          <span v-for="(_url, index) in recipe.image_urls" :key="index" class="dot"
            :class="{ active: index === currentImageIndex }" @click="setImage(index)"></span>
        </div>
      </div>

      <h3>Description</h3>
      <p>{{ recipe.description }}</p>

      <h3>Ingredients</h3>
      <p>{{ recipe.ingredients }}</p>

      <h3>Instructions</h3>
      <p>{{ recipe.instructions }}</p>
    </div>
  </div>
</template>

<style scoped>
.recipe-page {
  max-width: 800px;
  margin: auto;
  padding: 20px;
}

.carousel {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.carousel-image-container {
  position: relative;
  max-width: 100%;
}

.carousel-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 5px;
}

.fallback-container {
  position: relative;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 99%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: flex-end; /* Align items at the bottom */
  color: #b4a984;
  font-size: 14px;
}

.prev,
.next {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  padding: 10px;
  cursor: pointer;
  font-size: 18px;
  border-radius: 50%;
  z-index: 1;
}

.prev {
  left: 10px;
}

.next {
  right: 10px;
}

.indicators {
  position: absolute;
  bottom: 10px;
  width: 100%;
  text-align: center;
}

.dot {
  height: 10px;
  width: 10px;
  margin: 0 5px;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 25%;
  display: inline-block;
  cursor: pointer;
}

.dot.active {
  background-color: white;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.error {
  color: red;
}
</style>
