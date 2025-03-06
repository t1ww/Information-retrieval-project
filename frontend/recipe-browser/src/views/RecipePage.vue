<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute } from "vue-router";

interface RecipeDetail {
  recipe_id: string;
  name: string;
  description: string;
  ingredients: [string, string][];
  instructions: string[];
  image_urls: string[];
  author_name: string;
  calories: number;
  carbohydrate_content: number;
  cholesterol_content: number;
  cook_time: string;
  fat_content: number;
  fiber_content: number;
  protein_content: number;
  recipe_category: string;
  recipe_servings: number;
  sugar_content: number;
  prep_time: string;
  total_time: string;
  keywords: string[];
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
    <h1>{{ recipe?.name }}</h1>

    <div v-if="isLoading" class="loading">Loading...</div>
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <div v-if="recipe" class="recipe-details">
      <!-- Carousel -->
      <div class="carousel">
        <button v-if="recipe.image_urls.length > 1" class="prev" @click="prevImage">&#10094;</button>
        <div class="carousel-image-container">
          <transition name="fade" mode="out-in">
            <!-- Main Image Display -->
            <img v-if="recipe.image_urls.length > 0" :key="currentImageIndex" :src="recipe.image_urls[currentImageIndex]" :alt="recipe.name"
              class="carousel-image" />
            <!-- Fallback Image if no images are available -->
            <img v-else :src="fallbackImage" alt="Fallback Recipe Image" class="carousel-image" />
          </transition>
        </div>
        <button v-if="recipe.image_urls.length > 1" class="next" @click="nextImage">&#10095;</button>

        <!-- Indicators -->
        <div class="indicators">
          <span v-for="(_url, index) in recipe.image_urls" :key="index" class="dot"
            :class="{ active: index === currentImageIndex }" @click="setImage(index)"></span>
        </div>
      </div>

      <!-- Recipe Details -->
      <div class="recipe-info">
        <p><strong>Author:</strong> {{ recipe.author_name }}</p>
        <p><strong>Category:</strong> {{ recipe.recipe_category }}</p>
        <p><strong>Servings:</strong> {{ recipe.recipe_servings }}</p>
        <p><strong>Prep Time:</strong> {{ recipe.prep_time }}</p>
        <p><strong>Cook Time:</strong> {{ recipe.cook_time }}</p>
        <p><strong>Total Time:</strong> {{ recipe.total_time }}</p>

        <div class="nutrition">
          <p><strong>Calories:</strong> {{ recipe.calories }} kcal</p>
          <p><strong>Protein:</strong> {{ recipe.protein_content }} g</p>
          <p><strong>Carbohydrates:</strong> {{ recipe.carbohydrate_content }} g</p>
          <p><strong>Fat:</strong> {{ recipe.fat_content }} g</p>
          <p><strong>Fiber:</strong> {{ recipe.fiber_content }} g</p>
          <p><strong>Sugar:</strong> {{ recipe.sugar_content }} g</p>
          <p><strong>Cholesterol:</strong> {{ recipe.cholesterol_content }} mg</p>
        </div>
      </div>

      <h3>Description</h3>
      <p>{{ recipe.description }}</p>

      <h3>Ingredients</h3>
      <ul>
        <li v-for="(ingredient, index) in recipe.ingredients" :key="index">
          {{ ingredient[0] }}: {{ ingredient[1] }}
        </li>
      </ul>

      <h3>Instructions</h3>
      <ol>
        <li v-for="(instruction, index) in recipe.instructions" :key="index">{{ instruction }}</li>
      </ol>

      <h3>Keywords</h3>
      <div class="keywords">
        <span v-for="(keyword, index) in recipe.keywords" :key="index" class="keyword">{{ keyword }}</span>
      </div>
    </div>
  </div>
</template>


<style scoped>
.recipe-page {
  max-width: 800px;
  margin: auto;
  padding: 20px;
}

.loading {
  text-align: center;
  font-size: 18px;
}

.error {
  color: red;
  font-weight: bold;
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
  align-items: flex-end;
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

.recipe-info p {
  font-size: 16px;
  line-height: 1.5;
}

.nutrition p {
  font-size: 14px;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.keyword {
  background-color: #f1f1f1;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
  color: #555;
}
</style>
