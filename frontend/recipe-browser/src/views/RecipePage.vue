<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import type { RecipeDetailed as Recipe } from "@/type";
import RecipeList from "@/components/RecipeList.vue";

export default defineComponent({
  name: "RecipePage",
  setup() {
    const route = useRoute();
    const recipe = ref<Recipe | null>(null);
    const isLoading = ref<boolean>(true);
    const errorMessage = ref<string | null>(null);
    const bookmarkErrorMessage = ref<string | null>(null);
    const currentImageIndex = ref<number>(0);
    const fallbackImage = ref<string>("");
    const userRating = ref<number | null>(null); // Stores the user’s rating
    const isBookmarked = ref<boolean>(false);
    const recommendedRecipes = ref<Recipe[]>([]);
    const fallbackImageCache = new Map<string, string>(); // Cache fallback images by query

    // Fetch fallback image for recipes without images
    const fetchFallbackImage = async (query: string): Promise<string> => {
      if (fallbackImageCache.has(query)) {
        return fallbackImageCache.get(query) || "";
      }
      try {
        const response = await fetch(
          `http://localhost:5000/search_nearest_image?query=${encodeURIComponent(query)}`,
          {
            method: "GET",
            headers: { "Authorization": "dev" },
            credentials: "include",
          }
        );
        if (!response.ok) throw new Error(`Error fetching image: ${response.statusText}`);
        const imageData = await response.json();
        const imageUrl = imageData.result?.image_urls?.[0] || "";
        fallbackImageCache.set(query, imageUrl);
        return imageUrl;
      } catch (error) {
        console.error("Error fetching fallback image:", error);
        return "";
      }
    };

    // Fetch recipe details from the backend
    const fetchRecipe = async () => {
      isLoading.value = true;
      errorMessage.value = null;
      try {
        const response = await fetch(`http://localhost:5000/recipe/${route.params.id}`, {
          method: "GET",
          headers: { Authorization: "dev" },
          credentials: "include",
        });
        if (!response.ok) throw new Error(`Error: ${response.status} ${response.statusText}`);
        const data = await response.json();
        recipe.value = data;

        // Fetch bookmark status
        checkBookmarkStatus();

        // If no image is available, fetch the fallback image
        if (!data.image_urls || data.image_urls.length === 0) {
          fallbackImage.value = await fetchFallbackImage(data.name);
        }
      } catch (error) {
        errorMessage.value = (error as Error).message;
      } finally {
        isLoading.value = false;
      }
    };

    // Check if the recipe is already bookmarked
    const checkBookmarkStatus = async () => {
      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          console.error("No auth token found in localStorage");
          return;
        }
        const response = await fetch(`http://localhost:5000/bookmark_status?recipe_id=${route.params.id}`, {
          method: "GET",
          headers: { Authorization: token },
          credentials: "include",
        });
        if (!response.ok) throw new Error(`Failed to check bookmark status: ${response.statusText}`);
        const data = await response.json();
        isBookmarked.value = data.isBookmarked;
        userRating.value = data.rating || null;
      } catch (error) {
        console.error("Error checking bookmark status:", error);
      }
    };


    // Bookmark the recipe with a rating.
    // Prevents submission if no rating is selected.
    const bookmarkRecipe = async () => {
      if (userRating.value === null) {
        bookmarkErrorMessage.value = "Please select a rating before bookmarking.";
        return;
      }
      bookmarkErrorMessage.value = null; // Reset error if rating is set
      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          console.error("No auth token found in localStorage");
          return;
        }
        const response = await fetch("http://localhost:5000/bookmark", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: token,
          },
          credentials: "include",
          body: JSON.stringify({
            recipe_id: recipe.value?.recipe_id,
            rating: userRating.value,
          }),
        });
        if (!response.ok) throw new Error("Failed to bookmark recipe");
        isBookmarked.value = true;
      } catch (error) {
        console.error("Error bookmarking recipe:", error);
      }
    };

    // Fetch recommended recipes for the user
    const fetchRecommendations = async () => {
      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          console.error("No auth token found in localStorage");
          return;
        }

        const response = await fetch("http://localhost:5000/recommendations", {
          method: "GET",
          headers: { Authorization: token },
          credentials: "include",
        });

        if (!response.ok) throw new Error("Failed to fetch recommendations");

        const data = await response.json();
        recommendedRecipes.value = data.recommended_recipes;

        // Assign fallback image where needed
        const fallbackImg = await fetchFallbackImage(recipe.value?.name ?? "");
        recommendedRecipes.value = recommendedRecipes.value.map((rec: Recipe) => ({
          ...rec,
          image_urls: rec.image_urls.length ? rec.image_urls : [fallbackImg],
          fallback: rec.image_urls.length === 0,
        }));
      } catch (error) {
        console.error("Error fetching recommendations:", error);
      }
    };

    onMounted(() => {
      fetchRecipe();
      fetchRecommendations();
    });

    return {
      recipe,
      isLoading,
      errorMessage,
      currentImageIndex,
      fallbackImage,
      userRating,
      isBookmarked,
      bookmarkRecipe,
      recommendedRecipes,
      bookmarkErrorMessage
    };
  },
  components: {
    RecipeList
  },
});
</script>


<template>
  <div class="recipe-page">
    <h1 class="recipe-title">{{ recipe?.name }}</h1>

    <div v-if="isLoading" class="loading">Loading...</div>
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <div v-if="recipe" class="recipe-details">

      <!-- Image Section -->
      <div class="carousel">
        <img v-if="recipe.image_urls.length > 0" :src="recipe.image_urls[currentImageIndex]" :alt="recipe.name"
          class="carousel-image" />
        <div v-else class="fallback-container">
          <img :src="fallbackImage" alt="Fallback Recipe Image" />
          <div class="overlay">
            <span>*Taken from nearest image</span>
          </div>
        </div>
      </div>

      <!-- Bookmark Section -->
      <div class="bookmark-section">
        <div v-if="bookmarkErrorMessage" class="error-message">
          {{ bookmarkErrorMessage }}
        </div>
        <button v-if="isBookmarked" disabled class="bookmarked-btn">
          ✅ Bookmarked : {{ userRating }} ⭐
        </button>
        <div v-else>
          <label>Rate this Recipe: </label>
          <select v-model="userRating">
            <option :value="null" disabled>Select a rating</option>
            <option v-for="n in 5" :key="n" :value="n">{{ n }} ⭐</option>
          </select>
          <button @click="bookmarkRecipe">Bookmark</button>
        </div>
      </div>

      <!-- Recipe Information -->
      <div class="recipe-info">
        <p><strong>Author:</strong> {{ recipe.author_name }}</p>
        <p><strong>Category:</strong> {{ recipe.recipe_category }}</p>
        <p><strong>Servings:</strong> {{ recipe.recipe_servings }}</p>
        <p><strong>Preparation Time:</strong> {{ recipe.prep_time }}</p>
        <p><strong>Cook Time:</strong> {{ recipe.cook_time }}</p>
        <p><strong>Total Time:</strong> {{ recipe.total_time }}</p>
      </div>

      <!-- Snippet -->
      <section class="snippet">
        <h3>Description</h3>
        <p>{{ recipe.description }}</p>
      </section>

      <!-- Ingredients -->
      <section class="ingredients">
        <h3>Ingredients</h3>
        <ul>
          <li v-for="(ingredient, index) in recipe.ingredients" :key="index">
            {{ ingredient[0] }} : {{ ingredient[1] }}
          </li>
        </ul>
      </section>

      <!-- Instructions -->
      <section class="instructions">
        <h3>Instructions</h3>
        <ol>
          <li v-for="(step, index) in recipe.instructions" :key="index">
            {{ step }}
          </li>
        </ol>
      </section>

      <!-- Nutritional Information -->
      <section class="nutrition">
        <h3>Nutrition Facts</h3>
        <p><strong>Calories:</strong> {{ recipe.calories }} kcal</p>
        <p><strong>Carbohydrates:</strong> {{ recipe.carbohydrate_content }} g</p>
        <p><strong>Cholesterol:</strong> {{ recipe.cholesterol_content }} mg</p>
        <p><strong>Fat:</strong> {{ recipe.fat_content }} g</p>
        <p><strong>Fiber:</strong> {{ recipe.fiber_content }} g</p>
        <p><strong>Protein:</strong> {{ recipe.protein_content }} g</p>
        <p><strong>Sugar:</strong> {{ recipe.sugar_content }} g</p>
      </section>

    </div>

    <!-- Recommendations -->
    <section v-if="recommendedRecipes.length" class="recommendations">
      <h3>Recommended Recipes</h3>
      <RecipeList :recipes="recommendedRecipes" />
    </section>
  </div>
</template>

<style scoped>
.recipe-page {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  background: white;
  color: #242424;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recipe-title {
  text-align: center;
  font-size: 2.5em;
  margin-bottom: 20px;
}

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

.recipe-info,
.snippet,
.ingredients,
.instructions,
.nutrition {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  text-align: start;
}

h3 {
  color: #333;
  font-size: 1.5em;
}

ul,
ol {
  padding-left: 20px;
}

.bookmark-section {
  margin-top: 20px;
  text-align: center;
}

.bookmarked-btn {
  background-color: green;
  color: white;
  border: none;
  padding: 10px;
  cursor: not-allowed;
}

select {
  margin-right: 10px;
  padding: 5px;
  height: 2.5em;
}

.description {
  margin-top: 20px;
  text-align: left;
}

.recommendations {
  margin-top: 30px;
}

.error-message {
  color: red;
  margin-bottom: 10px;
}

.fallback-container {
  position: relative;
  display: inline-block;
}

.fallback-container img {
  width: 100%;
  height: auto;
  display: block;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  /* Darkens the image */
  z-index: 1;
  /* Ensure the overlay is above the image */
}

.overlay span {
  position: absolute;
  bottom: 10px;
  left: 50%;
  padding: .2em;
  transform: translateX(-50%);
  color: rgb(255, 213, 154);
  font-size: 14px;
  font-weight: bold;
  text-align: center;
  background: rgba(50, 32, 22, 0.5);
  /* Darkens the image */
  border-radius: .5em;
  z-index: 2;
  /* Ensure text is above the overlay */
}
</style>
