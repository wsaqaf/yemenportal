class Tags::Item::Cell < Application::Cell
  option :current_user
  property :description, :user, :created_at, :name, :post
end
