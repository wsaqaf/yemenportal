class PostsController < ApplicationController
  def index
    render cell: :index, model: posts
  end

  def show
    render cell: :show, model: post, layout: "post_layout"
  end

  private

  def post
    Post.find(params[:id])
  end

  def posts
    Posts::Filter.new(params).filtered_posts.includes(:related_posts)
  end
end
