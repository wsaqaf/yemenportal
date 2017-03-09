Rails.application.routes.draw do
  root to: 'home_page#index'

  resources :home_page, only: [:index]
  resources :categories, only: [:index, :new, :create, :destroy]
  resources :sources, only: [:index, :new, :create, :destroy]
  resources :moderators, only: [:index, :destroy]
end
