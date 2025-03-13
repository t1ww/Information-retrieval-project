<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import RecipeCard from "@/components/RecipeCard.vue";

interface Recipe {
  recipe_id: string;
  name: string;
  description: string;
  snippet: string;
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
  fallback?: boolean;
}

export default defineComponent({
  name: "RecipePage",
  setup() {
    const route = useRoute();
    const recipe = ref<Recipe | null>(null);
    const isLoading = ref<boolean>(true);
    const errorMessage = ref<string | null>(null);
    const currentImageIndex = ref<number>(0);
    const fallbackImage = ref<string>("");
    const userRating = ref<number | null>(null); // Stores the user’s rating
    const isBookmarked = ref<boolean>(false);
    const recommendedRecipes = ref<Recipe[]>([]);
    const fallbackImageCache = new Map<string, string>(); // Cache fallback images by query

    /**
     * Fetch recommended recipes for the user
     */
    const fetchRecommendations = async () => {
      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          console.error("No auth token found in localStorage");
          return;
        }

        const response = await fetch("http://localhost:5000/recommendations", {
          method: "GET",
          headers: {
            Authorization: token,
          },
          credentials: "include",
        });

        if (!response.ok) throw new Error("Failed to fetch recommendations");

        const data = await response.json();
        recommendedRecipes.value = data.recommended_recipes;

        // Assign fallback image where needed
        const fallbackImage = await fetchFallbackImage(recipe.value?.name ?? "food");
        recommendedRecipes.value = recommendedRecipes.value.map((recipe: Recipe) => ({
          ...recipe,
          image_urls: recipe.image_urls.length ? recipe.image_urls : [fallbackImage],
          fallback: recipe.image_urls.length === 0,
        }));
      } catch (error) {
        console.error("Error fetching recommendations:", error);
      }
    };


    /**
    * Fetch fallback image for recipes without images
    */
    const fetchFallbackImage = async (query: string): Promise<string> => {
      if (fallbackImageCache.has(query)) {
        return fallbackImageCache.get(query) || "";
      }
      try {
        const response = await fetch(`http://localhost:5000/search_nearest_image?query=${encodeURIComponent(query)}`, {
          method: "GET",
          headers: { "Authorization": "dev" },
          credentials: "include",
        });
        if (!response.ok) throw new Error(`Error fetching image: ${response.statusText}`);

        const imageData = await response.json();
        const imageUrl = imageData.result?.image_urls?.[0] || "";
        fallbackImageCache.set(query, imageUrl); // Store in cache
        return imageUrl;
      } catch (error) {
        console.error("Error fetching fallback image:", error);
        return "";
      }
    };

    /**
     * Fetch recipe details from the backend
     */
    const fetchRecipe = async () => {
      isLoading.value = true;
      errorMessage.value = null;
      try {
        const response = await fetch(`http://localhost:5000/recipe/${route.params.id}`, {
          method: "GET",
          headers: {
            Authorization: "dev",
          },
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

    /**
     * Check if the recipe is already bookmarked
     */
    const checkBookmarkStatus = async () => {
      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          console.error("No auth token found in localStorage");
          return;
        }

        const response = await fetch(`http://localhost:5000/bookmark_status?recipe_id=${route.params.id}`, {
          method: "GET",
          headers: {
            Authorization: token, // Make sure this is correct
          },
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


    /**
     * Bookmark the recipe with a rating
     */
    const bookmarkRecipe = async () => {
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
            Authorization: token, // Make sure this is correct
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

    onMounted(() => {
      fetchRecipe();
      fetchRecommendations(); // Fetch recommendations on page load
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
      recommendedRecipes
    };
  },
  components: {
    RecipeCard
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
        <img v-else :src="fallbackImage" alt="Fallback Recipe Image" class="carousel-image" />
      </div>

      <!-- Recipe Information -->
      <div class="recipe-info">
        <p><strong>Author:</strong> {{ recipe.author_name }}</p>
        <p><strong>Category:</strong> {{ recipe.recipe_category }}</p>
        <p><strong>Servings:</strong> {{ recipe.recipe_servings }}</p>
      </div>

      <!-- Bookmark Section -->
      <div class="bookmark-section">
        <button v-if="isBookmarked" disabled class="bookmarked-btn">✅ Bookmarked : {{ userRating }} ⭐</button>
        <div v-else>
          <label>Rate this Recipe:</label>
          <select v-model="userRating">
            <option :value="null" disabled>Select a rating</option>
            <option v-for="n in 5" :key="n" :value="n">{{ n }} ⭐</option>
          </select>
          <button @click="bookmarkRecipe">Bookmark</button>
        </div>
      </div>

      <!-- Description -->
      <section class="description">
        <h3>Description</h3>
        <p>{{ recipe.description }}</p>
      </section>
    </div>

    <!-- Recommendations -->
    <section v-if="recommendedRecipes.length" class="recommendations">
      <h3>Recommended Recipes</h3>
      <div class="recipe-list">
        <RecipeCard v-for="recipe in recommendedRecipes" :key="recipe.recipe_id" :recipe="recipe"
          :fallback="recipe.fallback" />
      </div>
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

/* Bookmark Section */
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
}

/* Description */
.description {
  margin-top: 20px;
  text-align: left;
}

/* Recommend section */
.recommendations {
  margin-top: 30px;
}

.recipe-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}
</style>
