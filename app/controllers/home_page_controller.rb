class HomePageController < ApplicationController
  def index
    category = Category.find_by(name: params[:category])
    if category
      posts = category.posts.paginate(page: params[:page], per_page: 20).order("pub_date DESC")
    else
      posts = Post.paginate(page: params[:page], per_page: 20).order("pub_date DESC")
    end
    render cell: true, model: posts, options: { categories: Category.all }
  end
end
