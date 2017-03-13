Rails.application.routes.draw do
  root to: 'home_page#index'

  resources :home_page, only: [:index]
  resources :categories, only: [:index, :new, :create, :destroy]
  resources :sources
  resources :moderators, only: [:index, :destroy]

  require 'sidekiq/web'
  Sidekiq::Web.set :session_secret, Rails.application.secrets[:secret_key_base]
  mount Sidekiq::Web, at: '/sidekiq'
end
