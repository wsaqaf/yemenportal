class PostsController < ApplicationController
  def index
    render cell: :index, model: posts
  end

  def show
    render cell: :show, model: post, layout: "post_layout"
  end

  private

  def post
    Post.include_voted_by_user(current_user).find(params[:id])
  end

  def posts
    Posts::Filter.new(params)
      .filtered_posts
      .includes(:related_posts)
      .include_voted_by_user(current_user)
  end
end
