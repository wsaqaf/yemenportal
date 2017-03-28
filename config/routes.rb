Rails.application.routes.draw do
  devise_for :users
  root to: 'posts#index'

  resources :categories, only: [:index, :new, :create, :destroy]
  resources :sources
  resources :moderators, only: [:index, :destroy]

  resources :posts, only: [:index, :show, :update]
  resource :votes, only: [:update]

  require 'sidekiq/web'
  Sidekiq::Web.set :session_secret, Rails.application.secrets[:secret_key_base]
  mount Sidekiq::Web, at: '/sidekiq'
end
