<script lang="ts">
import { defineComponent, ref, watch } from "vue";
import { useRouter } from "vue-router";

export default defineComponent({
  name: "SearchBar",
  props: {
    query: {
      type: String,
      default: "",
    },
  },
  setup(props) {
    const router = useRouter();
    const searchQuery = ref(props.query); // Use prop query to initialize the search input
    const errorMessage = ref(""); // To hold the error message

    const onSearchInput = () => {
      // Check if search query is empty
      if (searchQuery.value.trim() === "") {
        errorMessage.value = "Please enter a search query."; // Set error message
      } else {
        errorMessage.value = ""; // Clear any previous error
        router.push({ path: "/search", query: { query: searchQuery.value } });
      }
    };

    // Watch for changes to the searchQuery prop and update the local ref if needed
    watch(
      () => props.query,
      (newQuery) => {
        searchQuery.value = newQuery;
      }
    );

    return {
      onSearchInput,
      searchQuery,
      errorMessage,
    };
  },
});
</script>

<template>
  <!-- Display error message if input is empty -->
  <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  <div class="search-bar">
    <input
      type="text"
      v-model="searchQuery"
      placeholder="Search for a recipe..."
      @keydown.enter="onSearchInput"
    />
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
