class PostsController < ApplicationController
  def index
    render cell: :index, model: posts
  end

  def show
    post_view_registrar.commit_view
    show_post_page
  end

  private

  def posts
    Posts::Filter.new(params)
      .filtered_posts
      .includes(:related_posts, :categories)
      .include_voted_by_user(current_user)
  end

  def post_view_registrar
    @_post_view_registrar ||=
      PostViewRegistrar.new(post: post, user: current_user, user_ip: request.remote_ip)
  end

  def show_post_page
    if post.show_internally?
      render cell: :show, model: post, layout: "post_layout"
    else
      redirect_to post.link
    end
  end

  def post
    @_post ||= Post.include_voted_by_user(current_user).find(params[:id])
  end
end
