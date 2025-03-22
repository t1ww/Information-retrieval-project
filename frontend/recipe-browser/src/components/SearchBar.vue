<script lang="ts">
import { defineComponent, ref, watch, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

export default defineComponent({
  name: "SearchBar",
  setup() {
    const router = useRouter();
    const route = useRoute();

    // Use the route query parameters directly
    const searchQuery = ref(route.query.query || ""); // Initialize with query param
    const allergensQuery = ref(route.query.excluded_allergens || ""); // Initialize with excluded_allergens param
    const errorMessage = ref("");

    // Watch for changes in route query params
    watch(
      () => route.query.query,
      (newQuery) => {
        searchQuery.value = newQuery || "";
      }
    );

    watch(
      () => route.query.excluded_allergens,
      (newAllergens) => {
        allergensQuery.value = newAllergens || "";
        console.log('Updated allergensInput:', allergensQuery.value); // Debugging line
      }
    );

    // Ensure to initialize values on mount
    onMounted(() => {
      searchQuery.value = route.query.query || "";
      allergensQuery.value = route.query.excluded_allergens || "";
      console.log('Initial allergensInput:', allergensQuery.value); // Debugging line
    });

    const onSearchInput = () => {
      // Ensure that searchQuery is a string before calling trim
      const queryValue = typeof searchQuery.value === "string" ? searchQuery.value : "";

      if (queryValue.trim() === "") {
        errorMessage.value = "Please enter a search query.";
      } else {
        errorMessage.value = "";

        router.push({
          path: "/search",
          query: {
            query: queryValue,
            excluded_allergens: allergensQuery.value
          },
        });
      }
    };


    return {
      onSearchInput,
      searchQuery,
      allergensInput: allergensQuery,
      errorMessage,
    };
  },
});
</script>

<template>
  <!-- Display error message if input is empty -->
  <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  <div class="search-bar">
    <input type="text" v-model="searchQuery" placeholder="Search for a recipe..." @keydown.enter="onSearchInput" />
    <input type="text" v-model="allergensInput" placeholder="Exclude allergens (comma-separated)..."
      @keydown.enter="onSearchInput" />
    <button @click="onSearchInput" class="search-button">Search</button>
  </div>
</template>

<style scoped>
.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.search-bar input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-right: 10px;
}

.search-button {
  padding: 10px 15px;
  font-size: 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-button:hover {
  background-color: #45a049;
}

/* Error message style */
.error-message {
  color: red;
  font-size: 14px;
  margin-top: 10px;
}
</style>
