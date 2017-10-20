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
    Posts::Filter.new(user: current_user, params: params)
      .filtered_posts
      .includes(:posts_of_topic)
  end
end
