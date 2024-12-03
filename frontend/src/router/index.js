import { createRouter, createWebHistory } from 'vue-router'
import MoviesList from '@/components/MoviesList.vue'
import MovieDetails from '@/components/MovieDetails.vue'
import AddMovie from '@/components/AddMovie.vue'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: 'moviesList',
			component: MoviesList,
		},
		{
			path: '/movie/:id',
			component: MovieDetails,
			name: 'MovieDetails',
		},
		{
			path: '/add-movie',
			component: AddMovie,
		},
	],
})

export default router
