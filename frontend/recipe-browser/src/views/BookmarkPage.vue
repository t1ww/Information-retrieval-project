<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import RecipeCard from "@/components/RecipeCard.vue";

interface Recipe {
    recipe_id: string;
    name: string;
    snippet: string;
    image_urls: string[];
    fallback?: boolean;
}

export default defineComponent({
    name: "BookmarkPage",
    components: { RecipeCard },
    setup() {
        const bookmarks = ref<Recipe[]>([]);
        const folders = ref<{ [key: string]: Recipe[] }>({});
        const isLoading = ref<boolean>(true);
        const errorMessage = ref<string | null>(null);
        const newFolderName = ref<string>("");
        const fallbackImageCache = new Map<string, string>(); // Cache fallback images

        // Fetch fallback image logic
        const fetchFallbackImage = async (query: string): Promise<string> => {
            if (fallbackImageCache.has(query)) {
                return fallbackImageCache.get(query) || "";
            }
            try {
                const response = await fetch(`http://localhost:5000/search_nearest_image?query=${encodeURIComponent(query)}`, {
                    method: "GET",
                    headers: { Authorization: "dev" },
                    credentials: "include",
                });

                if (!response.ok) throw new Error("Error fetching fallback image");

                const imageData = await response.json();
                const imageUrl = imageData.result?.image_urls?.[0] || "";
                fallbackImageCache.set(query, imageUrl);
                return imageUrl;
            } catch (error) {
                console.error("Error fetching fallback image:", error);
                return "";
            }
        };

        // Fetch bookmarks
        const fetchBookmarks = async () => {
            try {
                const token = localStorage.getItem("authToken");
                if (!token) return;

                const response = await fetch("http://localhost:5000/bookmarks", {
                    method: "GET",
                    headers: { Authorization: token },
                    credentials: "include",
                });

                if (!response.ok) throw new Error("Failed to fetch bookmarks");

                const data = await response.json();

                const recipeDetails = await Promise.all(
                    data.bookmarks.map(async (bookmark: any) => {
                        const recipeResponse = await fetch(`http://localhost:5000/recipe/${bookmark.recipe_id}`, {
                            headers: { Authorization: token },
                            credentials: "include",
                        });

                        if (!recipeResponse.ok) return null;

                        const recipeData = await recipeResponse.json();
                        const fallbackImage = await fetchFallbackImage(recipeData.name);

                        return {
                            ...recipeData,
                            image_urls: recipeData.image_urls.length ? recipeData.image_urls : [fallbackImage],
                            fallback: recipeData.image_urls.length === 0,
                            rating: bookmark.rating,
                        };
                    })
                );

                bookmarks.value = recipeDetails.filter(Boolean);
            } catch (error) {
                errorMessage.value = (error as Error).message;
            } finally {
                isLoading.value = false;
            }
        };

        // Fetch folders
        const fetchFolders = async () => {
            try {
                const token = localStorage.getItem("authToken");
                if (!token) return;

                const response = await fetch("http://localhost:5000/folder_bookmarks", {
                    method: "GET",
                    headers: { Authorization: token },
                    credentials: "include",
                });

                if (!response.ok) throw new Error("Failed to fetch folders");

                const data = await response.json();
                const folderData: { [key: string]: Recipe[] } = {};

                for (const folderName in data) {
                    const recipeDetails = await Promise.all(
                        data[folderName].map(async (recipeId: number) => {
                            const recipeResponse = await fetch(`http://localhost:5000/recipe/${recipeId}`, {
                                headers: { Authorization: token },
                                credentials: "include",
                            });

                            if (!recipeResponse.ok) return null;

                            const recipeData = await recipeResponse.json();
                            const fallbackImage = await fetchFallbackImage(recipeData.name);

                            return {
                                ...recipeData,
                                image_urls: recipeData.image_urls.length ? recipeData.image_urls : [fallbackImage],
                                fallback: recipeData.image_urls.length === 0,
                            };
                        })
                    );

                    folderData[folderName] = recipeDetails.filter(Boolean);
                }

                folders.value = folderData;
            } catch (error) {
                console.error("Error fetching folders:", error);
            }
        };

        // Remove a bookmark
        const removeBookmark = async (recipeId: string) => {
            try {
                const token = localStorage.getItem("authToken");
                if (!token) return;

                const response = await fetch("http://localhost:5000/remove_bookmark", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: token,
                    },
                    credentials: "include",
                    body: JSON.stringify({ recipe_id: recipeId }),
                });

                if (!response.ok) throw new Error("Failed to remove bookmark");

                bookmarks.value = bookmarks.value.filter(b => b.recipe_id !== recipeId);
            } catch (error) {
                console.error("Error removing bookmark:", error);
            }
        };

        // Create a new folder
        const createFolder = async () => {
            if (!newFolderName.value.trim()) return;  // Prevent creating an empty folder

            const token = localStorage.getItem("authToken");
            if (!token) return;

            await fetch("http://localhost:5000/folders", {
                method: "POST",
                headers: { "Content-Type": "application/json", Authorization: token },
                credentials: "include",
                body: JSON.stringify({ folder_name: newFolderName.value }),
            });

            newFolderName.value = "";  // Clear the input field after creation
            fetchFolders();  // Refresh the folder list
        };

        // Initialize data
        onMounted(async () => {
            await fetchBookmarks();
            await fetchFolders();
        });

        return { bookmarks, folders, isLoading, errorMessage, removeBookmark, newFolderName, createFolder };
    },
});
</script>

<template>
    <div class="bookmark-page">
        <h1>Your Bookmarks</h1>

        <div v-if="isLoading">Loading...</div>
        <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

        <!-- Bookmarked Recipes -->
        <div v-if="bookmarks.length" class="recipe-list">
            <RecipeCard v-for="bookmark in bookmarks" :key="bookmark.recipe_id" :recipe="bookmark"
                :fallback="bookmark.fallback" />
            <button v-for="bookmark in bookmarks" :key="'remove' + bookmark.recipe_id"
                @click="removeBookmark(bookmark.recipe_id)">
                ❌ Remove
            </button>
        </div>
        <div v-else-if="!isLoading">No bookmarks yet.</div>

        <!-- Folders Section -->
        <section class="folders">
            <h3>Your Folders</h3>
            <div v-if="Object.keys(folders).length">
                <div v-for="(recipes, folder) in folders" :key="folder">
                    <h4>{{ folder }}</h4>
                    <div class="recipe-list">
                        <RecipeCard v-for="recipe in recipes" :key="recipe.recipe_id" :recipe="recipe"
                            :fallback="recipe.fallback" />
                    </div>
                </div>
            </div>
            <div v-else>No folders created yet.</div>

            <!-- Create Folder -->
            <h3>Create a New Folder</h3>
            <input v-model="newFolderName" placeholder="Folder name" />
            <button @click="createFolder">➕ Create</button>
        </section>
    </div>
</template>

<style scoped>
.recipe-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}

.folders {
    margin-top: 30px;
}

.error {
    color: red;
}
</style>
