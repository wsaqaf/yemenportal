require 'sidekiq/web'

Rails.application.routes.draw do
  devise_for :users, controllers: { omniauth_callbacks: "omniauth_callbacks", invitations: 'users/invitations',
    confirmations: 'users/confirmations' }
  root to: 'main_page#show'

  resources :categories, only: [:index, :new, :create, :destroy]
  resources :sources

  resources :topics, only: [:show] do
    scope module: :topics do
      resource :vote, only: [:update, :destroy]
      resources :comments, only: [:index]
      resources :reviews, only: [:index, :create, :destroy]
      resources :review_comments, only: [:create, :destroy]
    end
  end

  resources :posts, only: [:show]

  resources :users, only: [:index, :update, :edit] do
    scope module: :users do
      resource :moderator_permissions, only: [:create, :destroy]
      resource :admin_permissions, only: [:create, :destroy]
    end
  end

  namespace :sources do
    resources :approve, only: [:update]
    resources :suggest, only: [:create, :new]
  end

  resources :feedbacks, only: [:create]
  get "contact_us", to: "feedbacks#new", as: :new_feedback

  get "terms_of_use", to: "static_pages#terms_of_use"
  get "about_us", to: "static_pages#about_us"

  namespace :api do
    resources :sources, only: [:update]
  end

  authenticated :user, ->(user) { user.role.admin? } do
    Sidekiq::Web.set :session_secret, Rails.application.secrets[:secret_key_base]
    mount Sidekiq::Web, at: '/sidekiq'
  end
end
