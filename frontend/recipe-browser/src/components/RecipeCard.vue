<script lang="ts">
import { defineComponent } from 'vue'

interface Recipe {
  recipe_id: string
  name: string
  snippet: string
  image_urls: string[]
}

export default defineComponent({
  name: 'RecipeCard',
  props: {
    recipe: {
      type: Object as () => Recipe,
      required: true
    },
    fallback: {
      type: Boolean,
      default: false
    }
  }
})
</script>

<template>
  <div class="recipe-card">
    <div class="recipe-image">
      <template v-if="fallback && recipe.image_urls.length">
        <div class="fallback-container">
          <img :src="recipe.image_urls[0]" alt="Fallback Recipe Image" />
          <div class="overlay">
            <span>Taken from nearest image</span>
          </div>
        </div>
      </template>
      <template v-else-if="recipe.image_urls.length">
        <img :src="recipe.image_urls[0]" alt="Recipe Image" />
      </template>
      <template v-else>
        <div class="no-image">No Image</div>
      </template>
    </div>
    <div class="recipe-info">
      <h3>{{ recipe.name }}</h3>
      <p>{{ recipe.snippet }}</p>
    </div>
    <div class="recipe-actions">
      <router-link :to="`/recipe/${recipe.recipe_id}`">View Recipe</router-link>
    </div>
  </div>
</template>

<style scoped>
.recipe-card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.recipe-image {
  position: relative;
}

.recipe-image img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.fallback-container {
  position: relative;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-size: 14px;
}

.no-image {
  background-color: #f0f0f0;
  width: 100%;
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  font-size: 14px;
}

.recipe-info h3 {
  margin: 10px 0;
  font-size: 18px;
}

.recipe-info p {
  font-size: 14px;
  color: #555;
}

.recipe-actions a {
  margin-top: 10px;
  text-decoration: none;
  color: #007BFF;
  font-weight: bold;
}

.recipe-actions a:hover {
  text-decoration: underline;
}
</style>
