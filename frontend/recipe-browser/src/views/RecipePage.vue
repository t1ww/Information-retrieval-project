<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import type { Recipe, RecipeDetailed } from "@/type";
import RecipeList from "@/components/RecipeList.vue";

export default defineComponent({
  name: "RecipePage",
  setup() {
    const route = useRoute();
    const recipe = ref<RecipeDetailed | null>(null);
    const isLoading = ref<boolean>(true);
    const errorMessage = ref<string | null>(null);
    const bookmarkErrorMessage = ref<string | null>(null);
    const currentImageIndex = ref<number>(0);
    const fallbackImage = ref<string>("");
    const userRating = ref<number | null>(null); // Stores the user’s rating
    const isBookmarked = ref<boolean>(false);
    const recommendedRecipes = ref<Recipe[]>([]);
    const fallbackImageCache = new Map<string, string>(); // Cache fallback images by query
    const hasAuthToken = ref<boolean>(!!localStorage.getItem("authToken")); // Shows that logged in or not

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

        // Get the current recipe ID from route params
        const currentRecipeId = route.params.id; // Assuming the recipe ID is in the route params
        if (!currentRecipeId) {
          console.error("Current recipe ID is missing");
          return;
        }

        // Define the request options with optional headers
        const requestOptions: RequestInit = {
          method: "GET",
          credentials: "include",  // Include cookies for the request
        };

        if (token) {
          // If token exists, add Authorization header
          requestOptions.headers = {
            Authorization: token,
          };
        }

        // Fetch recommendations with the current recipe ID
        const response = await fetch(
          `http://localhost:5000/recommendations/current?current_recipe_id=${currentRecipeId}`,
          requestOptions
        );

        // If the response is not ok, throw an error
        if (!response.ok) throw new Error("Failed to fetch recommendations");

        // Parse the response JSON and store the recommended recipes
        const data = await response.json();
        recommendedRecipes.value = data.recommended_recipes;

      } catch (error) {
        // Catch and log any errors
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
      bookmarkErrorMessage,
      hasAuthToken
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
      <div v-if="hasAuthToken">
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
      </div>
      <div v-else>
        <p>Please login to bookmark a recipe.</p>
      </div>

      <!-- Allergens Warning -->
      <div v-if="recipe.allergens && recipe.allergens.length" class="allergens-warning">
        <strong>Contains :</strong> {{ recipe.allergens.join(', ') }}
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

    <!-- Recommendations Section -->
    <section v-if="recommendedRecipes.length > 0" class="recommendations">
      <h3>Recommended Recipes</h3>
      <RecipeList :recipes="recommendedRecipes" />
    </section>
    <section v-else class="no-recommendations">
      <p>No recommendations available at the moment.</p>
    </section>

  </div>
</template>

<style scoped>
.recipe-page {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  background: #1e1e1e;
  /* Dark background */
  color: #e0e0e0;
  /* Light text */
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.recipe-title {
  text-align: center;
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #ffffff;
}

.loading {
  text-align: center;
  font-size: 18px;
  margin: 20px 0;
  color: #e0e0e0;
}

.error {
  color: #ff6b6b;
  /* Light red for errors */
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
  background: #2a2a2a;
  /* Slightly lighter dark background */
  border-radius: 8px;
  text-align: left;
}

h3 {
  color: #ffffff;
  font-size: 1.5em;
}

ul,
ol {
  padding-left: 20px;
  color: #e0e0e0;
}

.bookmark-section {
  margin-top: 20px;
  text-align: center;
}

.bookmarked-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px;
  cursor: not-allowed;
}

select {
  margin-right: 10px;
  padding: 5px;
  height: 2.5em;
  background: #2a2a2a;
  color: #e0e0e0;
  border: 1px solid #444;
}

.description {
  margin-top: 20px;
  text-align: left;
}

.recommendations {
  margin-top: 30px;
}

.error-message {
  color: #ff6b6b;
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
  border-radius: 8px;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.overlay span {
  position: absolute;
  bottom: 10px;
  left: 50%;
  padding: 0.2em;
  transform: translateX(-50%);
  color: #ffd59a;
  font-size: 14px;
  font-weight: bold;
  text-align: center;
  background: rgba(50, 32, 22, 0.7);
  border-radius: 0.5em;
  z-index: 2;
}

/* Move actions to bottom */
.recipe-actions {
  margin-top: auto;
  text-align: center;
}

.recipe-actions a {
  margin-top: 10px;
  text-decoration: none;
  color: #90caf9;
  font-weight: bold;
}

.recipe-actions a:hover {
  text-decoration: underline;
}

/* Allergens warning style */
.allergens-warning {
  background-color: #ffe9a0;
  /* light yellow background */
  color: #856404;
  /* dark yellow text */
  padding: 4px 8px;
  border: 2px solid #ffd454;
  border-radius: 4px;
  margin-top: 8px;
  font-size: 16px;
}
</style>
