<script lang="ts">
import { defineComponent, ref, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import RecipeCard from "@/components/RecipeCard.vue";
import SearchBar from "@/components/SearchBar.vue";
import type { Recipe } from "@/type"

export default defineComponent({
  name: "SearchPage",
  components: {
    RecipeCard,
    SearchBar,
  },
  setup() {
    const route = useRoute();
    const searchQuery = ref<string>(String(route.query.query || route.query.q || "").trim());
    const recipes = ref<Recipe[]>([]);
    const isLoading = ref<boolean>(false);
    const errorMessage = ref<string | null>(null);
    const fallbackImageCache = new Map<string, string>(); // Cache fallback images by query

    /**
     * Fetch the fallback image for a query (uses caching)
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
     * Fetch recipes, ensuring fallback images are assigned when necessary
     */
    const fetchRecipes = async () => {
      const query = searchQuery.value.trim();
      if (!query) {
        recipes.value = [];
        return;
      }

      isLoading.value = true;
      errorMessage.value = null;

      try {
        // Get fallback image (cached if available)
        const fallbackImage = await fetchFallbackImage(query);

        // Fetch recipes
        const response = await fetch(`http://localhost:5000/search?query=${encodeURIComponent(query)}`, {
          method: "GET",
          headers: { "Authorization": "dev" },
          credentials: "include",
        });

        if (!response.ok) throw new Error(`Error: ${response.statusText}`);

        const data = await response.json();
        const fetchedRecipes = data.results || [];

        // Assign fallback image where needed
        recipes.value = fetchedRecipes.map((recipe: Recipe) => ({
          ...recipe,
          image_urls: recipe.image_urls.length ? recipe.image_urls : [fallbackImage],
          fallback: recipe.image_urls.length === 0,
        }));
      } catch (error) {
        errorMessage.value = (error as Error).message;
        recipes.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    /**
     * Watch for changes in the query and update recipes accordingly
     */
    watch(
      () => route.query.query || route.query.q,
      async (newQuery) => {
        if (newQuery && String(newQuery).trim() !== searchQuery.value) {
          searchQuery.value = String(newQuery).trim();
          fetchRecipes();
        }
      },
      { immediate: true } // Runs on initial mount
    );

    onMounted(fetchRecipes);

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
        :fallback="recipe.fallback"
      />
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
