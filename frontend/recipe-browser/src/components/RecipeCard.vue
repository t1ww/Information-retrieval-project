<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import type { Recipe } from '@/type';

const imageCache = new Map<string, string>(); // In-memory cache for images

export default defineComponent({
  name: 'RecipeCard',
  props: {
    recipe: {
      type: Object as () => Recipe,
      required: true,
    },
  },
  setup(props) {
    const fallbackImage = ref<string>(''); // Holds the fallback image URL
    const fallback = ref<boolean>(false); // Indicates whether a fallback is needed
    const cachedImage = ref<string>(''); // Holds the cached normal recipe image URL

    // Fetch fallback image for recipes without images
    const fetchFallbackImage = async (query: string): Promise<string> => {
      // Check if image is cached
      if (imageCache.has(query)) {
        return imageCache.get(query) || '';
      }

      try {
        const response = await fetch(
          `http://localhost:5000/search_nearest_image?query=${encodeURIComponent(query)}`,
          {
            method: 'GET',
            headers: { Authorization: 'dev' },
            credentials: 'include',
          }
        );
        if (!response.ok) throw new Error(`Error fetching image: ${response.statusText}`);
        const imageData = await response.json();
        const imageUrl = imageData.result?.image_urls?.[0] || '';

        // Cache the result
        imageCache.set(query, imageUrl);

        return imageUrl;
      } catch (error) {
        console.error('Error fetching fallback image:', error);
        return '';
      }
    };

    // Fetch and cache normal image
    const fetchNormalImage = async (imageUrl: string): Promise<string> => {
      // Check if normal image is already cached
      if (imageCache.has(imageUrl)) {
        return imageCache.get(imageUrl) || '';
      }

      try {
        const response = await fetch(imageUrl, { method: 'HEAD' });
        if (response.ok) {
          // Cache the normal image URL if it's valid
          imageCache.set(imageUrl, imageUrl);
          return imageUrl;
        }
      } catch (error) {
        console.error('Error fetching normal image:', error);
      }

      return '';
    };

    // If no image is available for the recipe, fetch the fallback image
    onMounted(async () => {
      if (props.recipe.image_urls && props.recipe.image_urls.length > 0) {
        // If the recipe has a normal image, fetch and cache it
        cachedImage.value = await fetchNormalImage(props.recipe.image_urls[0]);
      } else {
        // Otherwise, fetch the fallback image
        fallback.value = true;
        fallbackImage.value = await fetchFallbackImage(props.recipe.name);
      }
    });

    return {
      fallbackImage,
      fallback,
      cachedImage,
    };
  },
});
</script>


<template>
  <div class="recipe-card">
    <div class="recipe-image">
      <template v-if="fallback && fallbackImage">
        <div class="fallback-container">
          <img :src="fallbackImage" alt="Fallback Recipe Image" />
          <div class="overlay">
            <span>*Taken from nearest image</span>
          </div>
        </div>
      </template>
      <template v-else-if="recipe.image_urls && recipe.image_urls.length">
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
  height: 97%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: flex-end; /* Align items at the bottom */
  color: #b4a984;
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
