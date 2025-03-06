<script lang="ts">
import { defineComponent, ref, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import RecipeCard from "@/components/RecipeCard.vue";
import SearchBar from "@/components/SearchBar.vue";

interface Recipe {
  recipe_id: string;
  name: string;
  snippet: string;
  image_urls: string[];
  fallback_image?: string; // Fallback image URL
}

export default defineComponent({
  name: "SearchPage",
  components: {
    RecipeCard,
    SearchBar,
  },
  setup() {
    const route = useRoute();
    const searchQuery = ref<string>(String(route.query.query || route.query.q || ""));
    const recipes = ref<Recipe[]>([]);
    const isLoading = ref<boolean>(false);
    const errorMessage = ref<string | null>(null);
    const fallbackImage = ref<string>("");

    // Function to fetch the fallback image (only once per query)
    const fetchFallbackImage = async (): Promise<string> => {
      try {
        const response = await fetch(`http://localhost:5000/search_nearest_image?query=${encodeURIComponent(searchQuery.value)}`, {
          method: "GET",
          headers: {
            "Authorization": "dev", // Send the authorization token
          },
          credentials: "include", // If session-based auth is used
        });
        if (!response.ok) {
          throw new Error(`Error fetching image: ${response.status} ${response.statusText}`);
        }
        const imageData = await response.json();
        // Expecting imageData.result.image_urls to be an array
        if (imageData.result && imageData.result.image_urls && imageData.result.image_urls.length > 0) {
          return imageData.result.image_urls[0];
        }
        return "";
      } catch (error) {
        console.error("Error fetching fallback image:", error);
        return "";
      }
    };

    // Function to fetch recipes from the API
    const fetchRecipes = async () => {
      if (!searchQuery.value.trim()) {
        recipes.value = [];
        return;
      }
      isLoading.value = true;
      errorMessage.value = null;
      try {
        const response = await fetch(`http://localhost:5000/search?query=${encodeURIComponent(searchQuery.value)}`, {
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
        const fetchedRecipes = data.results || [];
        // Loop through each fetched recipe; if no image, assign fallback_image
        for (const recipe of fetchedRecipes) {
          if (recipe.image_urls.length === 0) {
            recipe.fallback_image = fallbackImage.value;
          }
        }
        recipes.value = fetchedRecipes;
      } catch (error) {
        errorMessage.value = (error as Error).message;
        recipes.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    // When the search query changes, first fetch the fallback image then fetch recipes
    watch(() => route.query.query || route.query.q, async (newQuery) => {
      searchQuery.value = String(newQuery || "");
      fallbackImage.value = await fetchFallbackImage();
      fetchRecipes();
    });

    // On page load, fetch the fallback image then the recipes
    onMounted(async () => {
      fallbackImage.value = await fetchFallbackImage();
      fetchRecipes();
    });

    return {
      searchQuery,
      recipes,
      isLoading,
      errorMessage,
    };
  },
});
</script>

<template>
  <div>
    <h1>Search Recipes</h1>
    <SearchBar :query="searchQuery" />

    <div v-if="isLoading">Loading...</div>
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <div v-if="recipes.length" class="recipe-list">
      <RecipeCard 
        v-for="recipe in recipes" 
        :key="recipe.recipe_id" 
        :recipe="recipe" 
        :fallback-image="recipe.fallback_image" />
    </div>
    <div v-else-if="!isLoading && !errorMessage">No recipes found.</div>
  </div>
</template>

<style scoped>
.recipe-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.error {
  color: red;
}
</style>
