Rails.application.routes.draw do
  resources :home_page, only: [:index]
end
