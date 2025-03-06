<script lang="ts">
import { defineComponent, ref, watch } from "vue";
import { useRoute } from "vue-router";
import RecipeCard from "@/components/RecipeCard.vue";
import SearchBar from "@/components/SearchBar.vue"; // Import the SearchBar component

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
    SearchBar, // Register the SearchBar component
  },
  setup() {
    const route = useRoute();
    const searchQuery = ref<string>(String(route.query.query || route.query.q || ""));

    // Watch for changes in the query params (for when the URL changes)
    watch(() => route.query.query || route.query.q, (newQuery) => {
      searchQuery.value = String(newQuery || "");
    });

    // Sample recipes data; replace with your API call as needed
    const recipes: Recipe[] = [
      {
        recipe_id: "88",
        name: "Breakfast Burritos",
        snippet: "Scramble eggs with a small amount of milk...",
        image_urls: [],
      },
      {
        recipe_id: "143",
        name: "Cherry Tomatoes on Provolone Garlic Bread",
        snippet: "For the tomatoes, mix tomatoes, scallions...",
        image_urls: [
          "https://img.sndimg.com/food/image/upload/w_555,h_416,c_fit,fl_progressive,q_95/v1/img/recipes/14/3/picBwpb8U.jpg",
        ],
      },
      {
        recipe_id: "54",
        name: "Carrot Cake",
        snippet: "Beat together the eggs, oil, and white sugar...",
        image_urls: [
          "https://img.sndimg.com/food/image/upload/w_555,h_416,c_fit,fl_progressive,q_95/v1/img/recipes/54/picQ2X4D8.jpg",
        ],
      },
    ];

    return {
      searchQuery,
      recipes,
    };
  },
});
</script>

<template>
  <div>
    <h1>Search Recipes</h1>
    <!-- Use the SearchBar component, passing the searchQuery prop -->
    <SearchBar :query="searchQuery"/>
    <!-- Recipes List -->
    <div class="recipe-list">
      <RecipeCard
        v-for="recipe in recipes"
        :key="recipe.recipe_id"
        :recipe="recipe"
      />
    </div>
  </div>
</template>

<style scoped>
.recipe-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}
</style>
