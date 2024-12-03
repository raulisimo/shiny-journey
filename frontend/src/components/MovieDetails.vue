<template>
	<div class="container mx-auto p-4">
		<!-- Movie Details Section -->
		<div v-if="movie" class="flex">
			<!-- Movie Image -->
			<div class="w-1/3">
				<img
					:src="movie.poster_url || defaultPoster"
					alt="Movie Poster"
					class="w-full h-full object-contain rounded-lg shadow-lg"
				/>
			</div>

			<!-- Movie Details -->
			<div class="w-2/3 pl-6">
				<h1 class="text-4xl font-semibold mb-4">{{ movie.title }}</h1>
				<p class="text-xl mb-2">
					<strong>Year:</strong> {{ movie.year }}
				</p>
				<p class="text-xl mb-4">
					<strong>Director:</strong> {{ movie.director }}
				</p>
				<p class="text-lg mb-6">{{ movie.plot }}</p>

				<!-- IMDb Link -->
				<a
					v-if="movie.imdb_id"
					:href="imdbLink"
					target="_blank"
					class="text-blue-600 hover:underline"
				>
					View on IMDb
				</a>
			</div>
		</div>

		<!-- Movie Not Found Message -->
		<div v-else>
			<h2 class="text-3xl text-red-600">Movie not found!</h2>
			<p class="text-lg text-gray-600">
				Sorry, the movie you're looking for does not exist.
			</p>
		</div>

		<!-- Loading Indicator -->
		<div v-if="loading" class="text-center text-xl text-gray-600">
			<p>Loading movie details...</p>
		</div>
	</div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { apiUrl } from '@/config'

export default {
	name: 'MovieDetails',
	setup() {
		const route = useRoute()
		const movieId = route.params.id
		const movie = ref(null)
		const loading = ref(true)
		const errorMessage = ref('')

		const defaultPoster = '/images/no-poster-available.jpg'

		// Build the IMDb link
		const imdbLink = computed(() => {
			return movie.value?.imdb_id
				? `https://www.imdb.com/title/${movie.value.imdb_id}`
				: ''
		})

		// Fetch movie details from the API
		const fetchMovieDetails = async () => {
			try {
				loading.value = true
				const response = await fetch(`${apiUrl}/movies/${movieId}`)
				if (response.ok) {
					const data = await response.json()
					movie.value = data
				} else {
					errorMessage.value = 'Movie not found!'
					movie.value = null
				}
			} catch (error) {
				errorMessage.value =
					'Error fetching movie details. Please try again later.'
				console.error('Error fetching movie details:', error)
				movie.value = null
			} finally {
				loading.value = false
			}
		}

		// Fetch movie details when the component is mounted
		onMounted(fetchMovieDetails)

		return {
			movie,
			loading,
			errorMessage,
			defaultPoster,
			imdbLink,
		}
	},
}
</script>

<style scoped>
/* Optional: Add styles for a smoother transition when hovering */
.movie-card {
	transition: transform 0.2s ease-in-out;
}

.movie-card:hover {
	transform: scale(1.05);
}
</style>
