require 'sidekiq/web'

Rails.application.routes.draw do
  devise_for :users, controllers: { omniauth_callbacks: "omniauth_callbacks", invitations: 'users/invitations',
    confirmations: 'users/confirmations' }
  root to: 'main_page#show'

  resources :categories, only: [:index, :new, :create, :destroy]
  resources :sources
  resources :topics, only: [:show]

  resources :post, only: [] do
    resources :comments, only: [:create, :destroy, :index]

    scope module: :posts do
      resources :tags, only: [:new, :create, :destroy, :index]
      resource :reader, only: [:show], controller: 'reader'
    end
  end

  resources :posts, only: [:index, :show, :update, :show]
  resources :users, only: [:index, :update, :edit] do
    scope module: :users do
      resource :moderator_permissions, only: [:create, :destroy]
      resource :admin_permissions, only: [:create, :destroy]
    end
  end
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
