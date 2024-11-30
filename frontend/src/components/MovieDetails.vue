<template>
  <div class="container mx-auto p-4">
    <div v-if="movie">
      <div class="flex">
        <!-- Movie Image -->
        <div class="w-1/3">
          <img
            :src="movie.poster_url || '/assets/images/404-poster.png'"
            alt="Movie Poster"
            class="w-full h-full object-contain rounded-lg shadow-lg"
          />
        </div>

        <!-- Movie Details -->
        <div class="w-2/3 pl-6">
          <h1 class="text-4xl font-semibold mb-4">{{ movie.title }}</h1>
          <p class="text-xl mb-2"><strong>Year:</strong> {{ movie.year }}</p>
          <p class="text-xl mb-4">
            <strong>Director:</strong> {{ movie.director }}
          </p>
          <p class="text-lg mb-6">{{ movie.plot }}</p>

          <!-- IMDb Link -->
          <a
            v-if="movie.imdb_id"
            :href="'https://www.imdb.com/title/' + movie.imdb_id"
            target="_blank"
            class="text-blue-600 hover:underline"
          >
            View on IMDb
          </a>
        </div>
      </div>
    </div>

    <!-- If movie not found, show not found message -->
    <div v-else>
      <h2 class="text-3xl text-red-600">Movie not found!</h2>
      <p class="text-lg text-gray-600">
        Sorry, the movie you're looking for does not exist.
      </p>
    </div>
  </div>
</template>

<script>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'

  export default {
    name: 'MovieDetails',
    setup() {
      const route = useRoute()
      const movieId = route.params.id
      const movie = ref(null)

      const fetchMovieDetails = async () => {
        try {
          const response = await fetch(
            `http://localhost:8000/api/movies/${movieId}`
          )
          if (response.ok) {
            const data = await response.json()
            movie.value = data
          } else {
            movie.value = null // Handle movie not found
          }
        } catch (error) {
          console.error('Error fetching movie details:', error)
          movie.value = null // Handle error
        }
      }

      onMounted(() => {
        fetchMovieDetails()
      })

      return {
        movie,
      }
    },
  }
</script>

<style scoped>
  /* Optional styling for better presentation */
  .movie-card {
    transition: transform 0.2s ease-in-out;
  }

  .movie-card:hover {
    transform: scale(1.05);
  }
</style>
