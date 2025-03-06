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

    // Function to fetch recipes from the API
    const fetchRecipes = async () => {
      if (!searchQuery.value.trim()) {
        recipes.value = [];
        return;
      }

      isLoading.value = true;
      errorMessage.value = null;
      try {
        const response = await fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent(searchQuery.value)}`, {
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
        recipes.value = data.results || []; // Fix here
      } catch (error) {
        errorMessage.value = (error as Error).message;
        recipes.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    // Fetch recipes when query changes
    watch(() => route.query.query || route.query.q, (newQuery) => {
      searchQuery.value = String(newQuery || "");
      fetchRecipes();
    });

    // Fetch recipes when the page loads
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
      <RecipeCard v-for="recipe in recipes" :key="recipe.recipe_id" :recipe="recipe" />
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
