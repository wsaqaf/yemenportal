Rails.application.routes.draw do
  root to: 'home_page#index'

  resources :home_page, only: [:index]
end
