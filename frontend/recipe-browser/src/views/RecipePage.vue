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
              "Authorization": "dev",
            },
            credentials: "include",
          }
        );
        if (!response.ok) {
          throw new Error(`Error fetching fallback image: ${response.status} ${response.statusText}`);
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
            "Authorization": "dev",
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
    <h1 class="recipe-title">{{ recipe?.name }}</h1>
    
    <div v-if="isLoading" class="loading">Loading...</div>
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
    
    <div v-if="recipe" class="recipe-details">
      <!-- Carousel Section -->
      <div class="carousel">
        <button v-if="recipe.image_urls.length > 1" class="prev" @click="prevImage">&#10094;</button>
        <div class="carousel-image-container">
          <transition name="fade" mode="out-in">
            <img 
              v-if="recipe.image_urls.length > 0" 
              :key="currentImageIndex" 
              :src="recipe.image_urls[currentImageIndex]" 
              :alt="recipe.name" 
              class="carousel-image" 
            />
            <img 
              v-else 
              :src="fallbackImage" 
              alt="Fallback Recipe Image" 
              class="carousel-image" 
            />
          </transition>
          <div v-if="!recipe.image_urls.length && fallbackImage" class="overlay">
            <span>*Taken from nearest image</span>
          </div>
        </div>
        <button v-if="recipe.image_urls.length > 1" class="next" @click="nextImage">&#10095;</button>
        <div v-if="recipe.image_urls.length > 1" class="indicators">
          <span 
            v-for="(_url, index) in recipe.image_urls" 
            :key="index" 
            class="dot" 
            :class="{ active: index === currentImageIndex }" 
            @click="setImage(index)"
          ></span>
        </div>
      </div>

      <!-- Recipe Information -->
      <div class="recipe-info">
        <div class="header-info">
          <p><strong>Author:</strong> {{ recipe.author_name }}</p>
          <p><strong>Category:</strong> {{ recipe.recipe_category }}</p>
          <p><strong>Servings:</strong> {{ recipe.recipe_servings }}</p>
        </div>
        <div class="time-info">
          <p><strong>Prep Time:</strong> {{ recipe.prep_time }}</p>
          <p><strong>Cook Time:</strong> {{ recipe.cook_time }}</p>
          <p><strong>Total Time:</strong> {{ recipe.total_time }}</p>
        </div>
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

      <!-- Description -->
      <section class="description">
        <h3>Description</h3>
        <p>{{ recipe.description }}</p>
      </section>

      <!-- Ingredients -->
      <section class="ingredients-section">
        <h3>Ingredients</h3>
        <ul class="ingredients">
          <li v-for="(ingredient, index) in recipe.ingredients" :key="index">
            <span class="quantity">{{ ingredient[1] }}</span>
            <span class="item">{{ ingredient[0] }}</span>
          </li>
        </ul>
      </section>

      <!-- Instructions -->
      <section class="instructions-section">
        <h3>Instructions</h3>
        <ol class="instructions">
          <li v-for="(instruction, index) in recipe.instructions" :key="index">
            {{ instruction }}
          </li>
        </ol>
      </section>

      <!-- Keywords -->
      <section class="keywords-section">
        <h3>Keywords</h3>
        <div class="keywords">
          <span v-for="(keyword, index) in recipe.keywords" :key="index" class="keyword">
            {{ keyword }}
          </span>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
/* Container styling */
.recipe-page {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  background: var(--app-bg, #ffffff);
  color: var(--app-text, #242424);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: system-ui, Avenir, Helvetica, Arial, sans-serif;
}

/* Title */
.recipe-title {
  text-align: center;
  font-size: 2.5em;
  margin-bottom: 20px;
}

/* Loading & error */
.loading {
  text-align: center;
  font-size: 18px;
  margin: 20px 0;
}
.error {
  color: red;
  text-align: center;
  margin-bottom: 20px;
}

/* Carousel styles */
.carousel {
  position: relative;
  margin-bottom: 20px;
}
.carousel-image-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}
.carousel-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 5px;
  transition: transform 0.3s ease-in-out;
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
  padding-bottom: 10px;
  color: #b4a984;
  font-size: 14px;
}

/* Carousel navigation */
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
  transition: background-color 0.3s;
}
.prev:hover,
.next:hover {
  background-color: rgba(0, 0, 0, 0.8);
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
  border-radius: 50%;
  display: inline-block;
  cursor: pointer;
  transition: background-color 0.3s;
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

/* Recipe info */
.recipe-info {
  margin: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.header-info,
.time-info,
.nutrition {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}
.header-info p,
.time-info p,
.nutrition p {
  margin: 0;
  font-size: 14px;
}

/* Sections */
.description,
.ingredients-section,
.instructions-section,
.keywords-section {
  margin-top: 20px;
  text-align: left;
}
h3 {
  font-size: 22px;
  margin-bottom: 10px;
  border-bottom: 2px solid #ccc;
  padding-bottom: 5px;
}

/* Ingredients */
.ingredients {
  list-style: none;
  padding: 0;
}
.ingredients li {
  padding: 5px 0;
  font-size: 16px;
}
.quantity {
  font-weight: bold;
  margin-right: 5px;
}

/* Instructions */
.instructions {
  padding-left: 20px;
  font-size: 16px;
  line-height: 1.5;
}

/* Keywords */
.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}
.keyword {
  background-color: #f1f1f1;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
  color: #555;
}
</style>
