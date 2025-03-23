<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import type { Recipe } from "@/type";
import RecipeList from "@/components/RecipeList.vue";
import Logo from "@/components/Logo.vue";
import SearchBar from "@/components/SearchBar.vue";

export default defineComponent({
  name: "HomePage",
  components: {
    SearchBar,
    Logo,
    RecipeList,
  },
  setup() {
    const recommendedRecipes = ref<Recipe[]>([]); // To store recommended recipes
    const loading = ref<boolean>(false); // To handle loading state
    const error = ref<string | null>(null); // To handle errors
    const playSound = ref<boolean>(true); // Only play the sound for the homepage logo
    const hasAuthToken = ref<boolean>(!!localStorage.getItem("authToken")); // Shows that logged in or not

    // Fetch bookmarked recommendations from the backend
    const fetchRecommendations = async () => {
      loading.value = true;
      error.value = null;

      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          console.error("No auth token found in localStorage");
          error.value = "No auth token found in localStorage";
          return;
        }

        // Fetching the bookmarked recommendations
        const response = await fetch("http://localhost:5000/recommendations/bookmarks", {
          method: "GET",
          headers: {
            "Authorization": `${token}`,  // Assuming token is set with 'Bearer' prefix
          },
          credentials: "include",  // Ensures cookies are included if necessary
        });

        // Check if the response is successful
        if (!response.ok) {
          throw new Error(`Failed to fetch: ${response.statusText}`);
        }

        // Parse the response JSON data
        const data = await response.json();

        // If no recommended recipes in the response, log and handle it
        if (!data.recommended_recipes) {
          console.error("No recommended recipes in response:", data);
          error.value = "No recommended recipes found.";
          return;
        }

        // Set the recommended recipes
        recommendedRecipes.value = data.recommended_recipes;

      } catch (err) {
        // Handle any error that occurred during the fetch
        console.error("Error fetching recommendations:", err);
        error.value = "Failed to fetch recommendations.";
      } finally {
        // Reset loading state
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchRecommendations();
    });

    return {
      playSound,
      recommendedRecipes,
      loading,
      error,
      hasAuthToken
    };
  },
});
</script>


<template>
  <Logo :play-sound="playSound" />
  <h1>Welcome to recipe browser</h1>
  <p>Start searching below!</p>

  <!-- Use the SearchBar component -->
  <SearchBar />

  <!-- Recommendations Section -->
  <section v-if="recommendedRecipes.length > 0" class="recommendations">
    <h3>Recommended Recipes</h3>
    <RecipeList :recipes="recommendedRecipes" />
  </section>
  <section v-else class="no-recommendations">
    <p v-if="hasAuthToken">No recommendations available at the moment.</p>
    <p v-else>
      Please login and bookmark a recipe to get recommendations.
    </p>
  </section>
</template>

<style scoped>
/* Add your styles for the HomePage if needed */
.error {
  color: red;
}
</style>
