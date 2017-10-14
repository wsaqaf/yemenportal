class PostsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def show
    render(
      cell: :show,
      model: post,
      layout: "post_layout",
      options: { host: params[:root] }
    )
  end

  private

  def post
    Post.find(params[:id])
  end
end
