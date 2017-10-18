class Posts::Flagging
  def initialize(moderator:, post:, flag:)
    @moderator = moderator
    @post = post
    @flag = flag
  end

  def create_review
    if flag.resolve?
      delete_all_other_reviews
    else
      delete_review_with_resolve_flag
    end
    create_review_instance
  end

  private

  attr_reader :moderator, :post, :flag

  def delete_all_other_reviews
    Review.where(post: post, moderator: moderator).destroy_all
  end

  def delete_review_with_resolve_flag
    Review.with_resolve_flag(post, moderator).destroy_all
  end

  def create_review_instance
    Review.create(moderator: moderator, post: post, flag: flag)
  end
end
