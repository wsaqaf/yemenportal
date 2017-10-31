class SourceProposalMailer < ApplicationMailer
  def notification(source:, submitter_email:)
    @source = source
    @submitter_email = submitter_email
    mail(
      to: User.admin_emails,
      subject: I18n.t("mailer.source_proposal.subject", source_name: @source.name)
    )
  end
end
