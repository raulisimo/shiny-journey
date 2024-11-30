<template>
  <div class="container mx-auto p-4">
    <!-- Search Bar -->
    <div class="mb-4">
      <input
        type="text"
        v-model="searchQuery"
        @input="searchMovies"
        class="px-4 py-2 rounded border border-gray-300 w-full md:w-1/2"
        placeholder="Search for a movie..."
      />
    </div>

    <!-- Movie Grid -->
    <div
      class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
    >
      <!-- If no movies, display a message -->
      <div
        v-if="movies.length === 0"
        class="col-span-4 text-center text-lg text-gray-500"
      >
        <p class="font-semibold text-2xl text-red-500">No movies found</p>
        <p class="text-sm text-gray-400">
          Try searching with a different title.
        </p>
      </div>

      <router-link
        v-for="movie in movies"
        :key="movie.id"
        :to="{ name: 'MovieDetails', params: { id: movie.id } }"
        class="bg-white rounded-lg shadow-lg overflow-hidden transform transition-transform duration-200 hover:scale-105"
      >
        <img
          :src="
            movie.poster_url || '/src/assets/images/no-poster-available.jpg'
          "
          alt="Movie Poster"
          class="w-full h-64 object-cover"
        />
        <div class="p-4">
          <h3 class="text-lg font-semibold">{{ movie.title }}</h3>
          <p class="text-sm text-gray-500">{{ movie.year }}</p>
        </div>
      </router-link>
    </div>

    <!-- Pagination -->
    <div class="mt-4 flex justify-center space-x-4">
      <!-- Previous Button -->
      <button
        @click="loadMovies(currentPage - 1)"
        :disabled="currentPage <= 1"
        class="px-4 py-2 bg-blue-500 text-white rounded-md transition duration-200 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        Previous
      </button>

      <!-- Pagination Info -->
      <span class="flex items-center text-lg">
        Page {{ currentPage }} of {{ totalPages }}
      </span>

      <!-- Next Button -->
      <button
        @click="loadMovies(currentPage + 1)"
        :disabled="currentPage >= totalPages"
        class="px-4 py-2 bg-blue-500 text-white rounded-md transition duration-200 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
  import { ref, onMounted } from 'vue'

  export default {
    name: 'MoviesList',
    setup() {
      const movies = ref([])
      const currentPage = ref(1)
      const totalPages = ref(1)
      const searchQuery = ref('')
      const errorMessage = ref('')

      // Function to load movies with pagination
      const loadMovies = async (page = 1) => {
        const limit = 10
        const response = await fetch(
          `http://localhost:8000/api/movies/?page=${page}&limit=${limit}`
        )
        const data = await response.json()
        movies.value = data.movies
        totalPages.value = data.total_pages
        currentPage.value = page
      }

      // Function to search movies by title
      const searchMovies = async () => {
        errorMessage.value = '' // Clear any previous error message
        if (!searchQuery.value) {
          loadMovies(1) // Load the first page of all movies if search is cleared
        } else {
          try {
            const response = await fetch(
              `http://localhost:8000/api/movies/search?title=${searchQuery.value}`
            )

            if (!response.ok) {
              if (response.status === 404) {
                movies.value = [] // No results found, clear movies
                errorMessage.value = 'No movies found' // Set error message
              }
              throw new Error('Movies not found')
            }

            const data = await response.json()
            movies.value = data
            totalPages.value = 1 // Since search results might be few, we set totalPages to 1
          } catch (error) {
            console.error(error)
            movies.value = [] // Clear movies on error (e.g., 404 not found)
            errorMessage.value = 'An error occurred. Please try again later.'
          }
        }
      }

      // Load movies on component mount
      onMounted(() => {
        loadMovies(currentPage.value)
      })

      return {
        movies,
        loadMovies,
        currentPage,
        totalPages,
        searchQuery,
        searchMovies,
        errorMessage,
      }
    },
  }
</script>
