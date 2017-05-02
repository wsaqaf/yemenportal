require 'sidekiq/web'

Rails.application.routes.draw do
  devise_for :users, controllers: { omniauth_callbacks: "omniauth_callbacks", invitations: 'users/invitations',
    confirmations: 'users/confirmations' }
  root to: 'posts#index'

  resources :categories, only: [:index, :new, :create, :destroy]
  resources :sources
  resources :moderators, only: [:index, :destroy]

  resources :moderators, only: [] do
    scope module: :moderators do
      resources :invites, only: [:create]
    end
  end

  resources :posts, only: [:index, :show, :update]
  resources :users, only: [:update, :edit]
  resource :votes, only: [:update]

  namespace :sources do
    resources :approve, only: [:update]
    resources :suggest, only: [:create, :new]
  end

  namespace :api do
    resources :sources, only: [:update]
  end

  authenticated :user, ->(user) { user.role.admin? } do
    Sidekiq::Web.set :session_secret, Rails.application.secrets[:secret_key_base]
    mount Sidekiq::Web, at: '/sidekiq'
  end
end
