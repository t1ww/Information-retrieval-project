<script lang="ts">
import { defineComponent, ref, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import RecipeList from "@/components/RecipeList.vue";
import SearchBar from "@/components/SearchBar.vue";
import type { Recipe } from "@/type";

export default defineComponent({
  name: "SearchPage",
  components: {
    RecipeList,
    SearchBar,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const searchQuery = ref<string>(String(route.query.query || route.query.q || "").trim());
    const allergensQuery = ref<string>(String(route.query.excluded_allergens || "").trim()); // Track allergensQuery
    const suggestedQuery = ref<string | null>(null); // Store suggested query
    const recipes = ref<Recipe[]>([]);
    const isLoading = ref<boolean>(false);
    const errorMessage = ref<string | null>(null);

    // Fetch recipes with query and allergensQuery
    const fetchRecipes = async () => {
      const query = searchQuery.value.trim();
      const excludedAllergens = allergensQuery.value.trim();

      if (!query) {
        recipes.value = [];
        suggestedQuery.value = null;
        return;
      }

      isLoading.value = true;
      errorMessage.value = null;

      try {
        const response = await fetch(`http://localhost:5000/search?query=${encodeURIComponent(query)}&excluded_allergens=${encodeURIComponent(excludedAllergens)}`, {
          method: "GET",
          credentials: "include",
        });

        if (!response.ok) throw new Error(`Error: ${response.statusText}`);

        const data = await response.json();
        const fetchedRecipes = data.results || [];

        // Store suggested query without applying it
        suggestedQuery.value = data.suggested_query || null;

        // Directly assign recipes
        recipes.value = fetchedRecipes.map((recipe: Recipe) => ({
          ...recipe,
          fallbackImage: false, // No fallback image handling anymore
        }));
      } catch (error) {
        errorMessage.value = (error as Error).message;
        recipes.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    // User accepts the suggested query
    const applySuggestedQuery = () => {
      if (suggestedQuery.value) {
        searchQuery.value = suggestedQuery.value;
        suggestedQuery.value = null; // Stop showing suggestions after applying

        setTimeout(() => {
          router.replace({ query: { query: searchQuery.value, excluded_allergens: allergensQuery.value } });
          fetchRecipes();
        }, 100);
      }
    };

    // Watch for query changes in the URL and fetch data
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

    // Watch for allergensQuery changes in the URL and fetch data
    watch(
      () => route.query.excluded_allergens,
      async (newAllergens) => {
        const newAllergensTrimmed = String(newAllergens || "").trim(); // Ensure it's treated as a trimmed string
        if (newAllergensTrimmed !== allergensQuery.value) {
          allergensQuery.value = newAllergensTrimmed; // Update the allergensQuery
          fetchRecipes(); // Fetch new recipes with updated allergensQuery
        }
      },
      { immediate: true } // Runs on initial mount
    );

    onMounted(fetchRecipes);

    return {
      searchQuery,
      allergensQuery, // Add allergensQuery to the return
      suggestedQuery,
      recipes,
      isLoading,
      errorMessage,
      applySuggestedQuery,
    };
  },
});
</script>

<template>
  <div>
    <h1>Search Recipes</h1>
    <SearchBar :query="searchQuery" :excludedAllergens="allergensQuery" />

    <div v-if="isLoading">Loading...</div>
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <!-- Suggested Query Display -->
    <div v-if="suggestedQuery && suggestedQuery !== searchQuery" class="suggestion">
      Did you mean:
      <button @click="applySuggestedQuery" class="suggested-btn">{{ suggestedQuery }}</button>?
    </div>

    <div v-if="recipes.length" class="recipe-list">
      <RecipeList :recipes="recipes" />
    </div>
    <div v-else-if="!isLoading && !errorMessage">No recipes found.</div>
  </div>
</template>

<style scoped>
div {
  width: 100%;
}

.error {
  color: red;
}

.suggestion {
  margin: 10px 0;
  font-size: 1.1em;
}

.suggested-btn {
  background: none;
  border: none;
  color: blue;
  text-decoration: underline;
  cursor: pointer;
  font-size: 1.1em;
}

.suggested-btn:hover {
  color: darkblue;
}
</style>
